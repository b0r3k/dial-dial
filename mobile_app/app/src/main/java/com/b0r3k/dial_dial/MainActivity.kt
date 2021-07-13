package com.b0r3k.dial_dial

import android.app.Activity
import android.content.ContentResolver
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.ContactsContract.CommonDataKinds.Phone
import android.speech.RecognizerIntent
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import android.util.Log
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts.RequestMultiplePermissions
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.b0r3k.dial_dial.databinding.ActivityMainBinding
import com.ibm.cloud.sdk.core.security.IamAuthenticator
import com.ibm.watson.assistant.v2.Assistant
import com.ibm.watson.assistant.v2.model.*
import kotlinx.coroutines.*
import kotlinx.coroutines.Dispatchers.IO
import kotlinx.coroutines.Dispatchers.Main
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import java.util.*


class MainActivity : AppCompatActivity() {
    private var mainActBinding: ActivityMainBinding? = null
    private var sessionId: String? = null
    private var assistant: Assistant? = null
    private var speechRecognizerIntent: Intent? = null
    private var watsonReadyDeferred: Deferred<Boolean>? = null
    private var watsonReady: Boolean? = null
    private var contacts: Map<String, String>? = null
    private var textToSpeech: TextToSpeech? = null
    private var launchAgain: Boolean = true
    private var callIntent: Intent? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Binding for communication with UI
        mainActBinding = ActivityMainBinding.inflate(layoutInflater)

        // Intent to recognize speech in Czech
        speechRecognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "cs-CZ")
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }

        // Component for speech synthesis in Czech, overriding OnDone function to trigger actions
        // after TTS finishes
        textToSpeech = TextToSpeech(this, TextToSpeech.OnInitListener {
            if (it == TextToSpeech.SUCCESS) {
                textToSpeech!!.language = Locale("cs_CZ")
                textToSpeech!!.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(utteranceId: String?) {}

                    override fun onDone(utteranceId: String?) {
                        CoroutineScope(Main).launch {
                            if (launchAgain) {
                                // Launch the STT and whole pipeline again
                                launchPipeline()
                            } else {
                                // Start call
                                startActivity(callIntent!!)
                                // End the WA session
                                withContext(IO) {
                                    val options = DeleteSessionOptions.Builder(
                                        getString(R.string.waston_assistant_id),
                                        sessionId
                                    ).build()
                                    assistant!!.deleteSession(options).execute()
                                }
                                // End this app
                                finish()
                            }
                        }
                    }

                    override fun onError(utteranceId: String?) {}
                })
            } else {
                Toast.makeText(
                    applicationContext,
                    getString(R.string.toast_tts_init_fail),
                    Toast.LENGTH_SHORT
                ).show()
            }
        })

        // Set the button click
        mainActBinding?.ivCircle?.setOnClickListener {
            if (checkPermissions()) {
                // If not ready start asynchronously preparing Watson
                if ((watsonReady == null) or (watsonReady == false)) {
                    // Launch in IO, network request
                    watsonReadyDeferred = CoroutineScope(IO).async {
                        return@async tryPrepareWatson()
                    }
                }
                // Launch speech recognition, on result watson is contacted
                launchPipeline()
                // Disable the button
                mainActBinding?.ivCircle?.isEnabled = false
            }
        }

        // Set the view in UI
        setContentView(mainActBinding?.root)
    }

    private fun launchPipeline() {
        /**
         * Launches the STT and on result the whole pipeline for communication with user.
         */
        mainActBinding?.ivSpeak?.setImageResource(R.drawable.ic_mic_full_red)
        pipelineLauncher.launch(speechRecognizerIntent)
    }

    // Launcher with registered callback on activity end (when STT ends)
    private val pipelineLauncher =
        registerForActivityResult(StartActivityForResult()) { activityResult ->
            mainActBinding?.ivSpeak?.setImageResource(R.drawable.ic_mic_empty)
            if (activityResult.resultCode == Activity.RESULT_OK) {
                // Get result from STT, check if valid
                val result =
                    activityResult.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
                if (!result.isNullOrEmpty()) {
                    val textResult = result[0].toString()
                    // Launch in IO, network request
                    CoroutineScope(IO).launch {
                        // Await Watson preparation, if ready get response
                        var response = ""
                        watsonReady = watsonReadyDeferred!!.await()
                        if (watsonReady!!) {
                            response = getWatsonResponse(textResult)
                        } else {
                            response = getString(R.string.watson_init_failed)
                        }
                        withContext(Main) {
                            // Check the response, decide what next
                            val tokens = response.split('\n')
                            var textToRead = tokens[0]
                            if (tokens.size > 1 && tokens[0] == "[call]") {
                                // We should call, prepare Intent, not launchAgain
                                textToRead = tokens[2]
                                launchAgain = false
                                val contact = tokens[1]
                                val number = contacts!![contact]
                                callIntent = Intent(Intent.ACTION_CALL).apply {
                                    data = Uri.parse("tel:$number")
                                }
                            }
                            mainActBinding?.ivSpeak?.setImageResource(R.drawable.ic_sound)
                            // Synthesise and play the response with TTS
                            textToSpeech!!.speak(
                                textToRead,
                                TextToSpeech.QUEUE_FLUSH,
                                null,
                                "WATSON_TTS"
                            )
                        }
                    }
                }
            }
        }

    private fun getWatsonResponse(message: String): String {
        /**
         * Returns Watson answer for given [message]. Uses sessionId from Activity and
         * watson_assistant_id from resources. Must run in coroutine, because is network request!
         */
        val messageInput = MessageInput.Builder().messageType("text").text(message).build()
        val messageOptions =
            MessageOptions.Builder(getString(R.string.waston_assistant_id), sessionId)
                .input(messageInput).build()
        val response = assistant!!.message(messageOptions).execute().result
        var textResponse: String = ""
        if (response.output.generic.isNotEmpty()) {
            textResponse = response.output.generic[0].text().toString()
        }
        return textResponse
    }

    private suspend fun tryPrepareWatson(): Boolean {
        /**
         * Returns whether Watson initialization was successful. Is suspend function, uses network
         * request, so must run in coroutine.
         * At the beginning calls loadContacts to retrieve contacts, then creates Watson session.
         * Then awaits contacts and sends them as context to Watson.
         */
        try {
            val contactsReadyDeferred = CoroutineScope(IO).async {
                // Start asynchronously retrieving contacts
                return@async loadContacts()
            }
            // Initiate Watson session
            val authenticator =
                IamAuthenticator(getString(R.string.watson_assistant_apikey))
            val headers = mapOf("X-Watson-Learning-Opt-Out" to "true")
            assistant = Assistant("2021-06-22", authenticator).apply {
                serviceUrl = getString(R.string.watson_assistant_url)
                setDefaultHeaders(headers)
            }
            val options =
                CreateSessionOptions.Builder(getString(R.string.waston_assistant_id))
                    .build()
            val response = assistant!!.createSession(options).execute().result
            sessionId = response.sessionId

            // Await the contacts
            val contactsReady = contactsReadyDeferred.await()
            if (contactsReady) {
                // If successfully retrieved contacts, send them to Watson as context
                val contactsJson = Json.encodeToString(contacts!!.keys)
                val contactsStringSend = "{ \"__contacts__\" : $contactsJson }"

                val userDefinedContext: MutableMap<String, Any> = HashMap()
                userDefinedContext["contacts"] = contactsStringSend
                val dailSkillContext =
                    MessageContextSkill.Builder().userDefined(userDefinedContext).build()
                val skillsContext: MutableMap<String, MessageContextSkill> = HashMap()
                skillsContext["main skill"] =
                    dailSkillContext // name of the skill `dial_dial_cz` does not work!!

                val context = MessageContext.Builder().skills(skillsContext).build()

                val messageOptions =
                    MessageOptions.Builder(getString(R.string.waston_assistant_id), sessionId)
                        .context(context).build()
                assistant!!.message(messageOptions).execute()
            } else {
                return false
            }
        } catch (e: Exception) {
            return false
        }
        return true
    }

    private fun loadContacts(): Boolean {
        /**
         * Loads contacts (with telephone numbers) from Database-like Android storage. Saves them
         * into a Map. Returns true after operation finish.
         */
        var result: MutableMap<String, String> = mutableMapOf()
        val URI: Uri = Phone.CONTENT_URI
        val PROJECTION: Array<out String> = arrayOf(
            Phone.CONTACT_ID,
            Phone.DISPLAY_NAME,
            Phone.NUMBER
        )
        val contentResolver: ContentResolver = applicationContext.contentResolver
        val cursor = contentResolver.query(URI, PROJECTION, null, null, null)
        while ((cursor != null) and (cursor!!.moveToNext())) {
            val name: String = cursor.getString(1)
            val number: String = cursor.getString(2)
            result[name] = number
        }
        cursor.close()
        contacts = result
        return true
    }

    // Launcher with registered callback on activity end (when permission request ends)
    private val requestPermissionLauncher =
        registerForActivityResult(RequestMultiplePermissions()) { results: Map<String, Boolean> ->
            if (results.values.all { it }) {
                // All permissions granted, fine
                Toast.makeText(applicationContext, getString(R.string.toast_permissions_granted), Toast.LENGTH_SHORT)
                    .show()
            } else {
                // Some permission not granted, show that app is unavailable
                showUnavailableDialog()
            }
        }

    private fun checkPermissions(): Boolean {
        /**
         * Returns whether all necessary permissions are granted. If not, either shows explanation
         * why we need permissions, or requests the permissions.
         */
        val permissions = arrayOf(
            android.Manifest.permission.RECORD_AUDIO,
            android.Manifest.permission.READ_CONTACTS,
            android.Manifest.permission.CALL_PHONE
        )
        when {
            permissions.all {
                ActivityCompat.checkSelfPermission(
                    applicationContext,
                    it
                ) == PackageManager.PERMISSION_GRANTED
            } -> {
                // All permissions granted
                return true
            }
            permissions.any { shouldShowRequestPermissionRationale(it) } -> {
                // Some permission already requested but not given, explain and request again
                showRationaleDialog(permissions)
            }
            else -> {
                // Some permission not granted and not requested, request
                requestPermissionLauncher.launch(permissions)
            }
        }
        return false
    }

    private fun showRationaleDialog(permissions: Array<String>) {
        /**
         * Shows AlertDialog explaining why we need permissions, on OK requests permissions again.
         */
        val builder = AlertDialog.Builder(this)

        builder.apply {
            setMessage(getString(R.string.explain_why_permissions))
            setTitle(getString(R.string.need_permissions))
            setPositiveButton("OK") { _, _ ->
                // Request permissions again
                requestPermissionLauncher.launch(permissions)
            }
        }
        val dialog = builder.create()
        // Show the dialog
        dialog.show()
    }

    private fun showUnavailableDialog() {
        /**
         * Shows AlertDialog explaining that without permissions we can't work.
         */
        val builder = AlertDialog.Builder(this)

        builder.apply {
            setMessage(getString(R.string.explain_without_permissions))
            setTitle(getString(R.string.need_permissions))
            setPositiveButton("OK") { _, _ -> }
        }
        val dialog = builder.create()
        // Show the dialog
        dialog.show()
    }
}