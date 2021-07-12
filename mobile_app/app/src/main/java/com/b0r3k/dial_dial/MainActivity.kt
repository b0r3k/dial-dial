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
    private var sessionId : String? = null
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
        mainActBinding = ActivityMainBinding.inflate(layoutInflater)

        speechRecognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "cs-CZ")
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }

        textToSpeech = TextToSpeech(this, TextToSpeech.OnInitListener {
            if (it == TextToSpeech.SUCCESS) {
                Log.i("TTS", "Initialization success")
                textToSpeech!!.language = Locale("cs_CZ")
                textToSpeech!!.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(utteranceId: String?) { }

                    override fun onDone(utteranceId: String?) {
                        CoroutineScope(Main).launch {
                            if (launchAgain) {
                                launchPipeline()
                            }
                            else {
                                startActivity(callIntent!!)

                                withContext(IO) {
                                    val options = DeleteSessionOptions.Builder(
                                        getString(R.string.waston_assistant_id),
                                        sessionId
                                    ).build()
                                    assistant!!.deleteSession(options).execute()
                                }

                                finish()
                            }
                        }
                    }

                    override fun onError(utteranceId: String?) { }
                })
            }
            else {
                Log.i("TTS", "Initialization failed")
                Toast.makeText(applicationContext, "Text to speech initialization failed.", Toast.LENGTH_SHORT).show()
            }
        })

        mainActBinding?.ivCircle?.setOnClickListener {
            if (checkPermissions()) {
                // If not ready, prepare watson
                if ((watsonReady == null) or (watsonReady == false)) {
                    watsonReadyDeferred = CoroutineScope(IO).async {
                        return@async tryPrepareWatson()
                    }
                }
                // Launch speech recognition, on result watson is contacted
                launchPipeline()
            }
        }
        setContentView(mainActBinding?.root)
    }

    private fun launchPipeline() {
        mainActBinding?.ivSpeak?.setImageResource(R.drawable.ic_mic_full_red)
        pipelineLauncher.launch(speechRecognizerIntent)
    }

    private val pipelineLauncher = registerForActivityResult(StartActivityForResult()) {
            activityResult ->
        mainActBinding?.ivSpeak?.setImageResource(R.drawable.ic_mic_empty)
        if (activityResult.resultCode == Activity.RESULT_OK) {
            val result =
                activityResult.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if (!result.isNullOrEmpty()) {
                val textResult = result[0].toString()
                Log.i("tag", textResult)
                CoroutineScope(IO).launch {
                    var response = ""
                    watsonReady = watsonReadyDeferred!!.await()
                    if (watsonReady!!) {
                        response = getWatsonResponse(textResult)
                    }
                    else {
                        response = "Bohužel, při inicilaizaci se něco nepovedlo."
                    }
                    withContext(Main) {
                        Log.i("tag", response)
                        val tokens = response.split('\n')
                        var textToRead = tokens[0]
                        if (tokens.size > 1 && tokens[0] == "[call]") {
                            textToRead = tokens[2]
                            launchAgain = false
                            val contact = tokens[1]
                            val number = contacts!![contact]
                            Log.i("tag", "Calling contact $contact with number $number")
                            callIntent = Intent(Intent.ACTION_CALL).apply {
                                data = Uri.parse("tel:$number")
                            }
                        }
                        textToSpeech!!.speak(textToRead, TextToSpeech.QUEUE_FLUSH, null, "WATSON_TTS")
                    }
                }
            }
        }
    }

    private fun getWatsonResponse(message: String): String {
        val messageInput = MessageInput.Builder().messageType("text").text(message).build()
        val messageOptions = MessageOptions.Builder(getString(R.string.waston_assistant_id), sessionId).input(messageInput).build()
        val response = assistant!!.message(messageOptions).execute().result
        var textResponse: String = ""
        if (response.output.generic.isNotEmpty()) {
            textResponse = response.output.generic[0].text().toString()
        }
        return textResponse
    }

    private suspend fun tryPrepareWatson(): Boolean {
        try {
            val contactsReadyDeferred = CoroutineScope(IO).async {
                return@async loadContacts()
            }
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

            val contactsReady = contactsReadyDeferred.await()
            if (contactsReady) {
                val contactsJson = Json.encodeToString(contacts!!.keys)
                Log.i("tag", contactsJson)
                val contactsStringSend = "{ \"__contacts__\" : $contactsJson }"

                val userDefinedContext: MutableMap<String, Any> = HashMap()
                userDefinedContext["contacts"] = contactsStringSend
                val dailSkillContext = MessageContextSkill.Builder().userDefined(userDefinedContext).build()
                val skillsContext: MutableMap<String, MessageContextSkill> = HashMap()
                skillsContext["main skill"] = dailSkillContext // name of the skill `dial_dial_cz` does not work!!

                val context = MessageContext.Builder().skills(skillsContext).build()

                val messageOptions = MessageOptions.Builder(getString(R.string.waston_assistant_id), sessionId).context(context).build()
                assistant!!.message(messageOptions).execute()
            }
            else {
                return false
            }
        } catch (e: Exception) {
            Log.i("tag", e.toString())
            return false
        }
        return true
    }

    private fun loadContacts(): Boolean {
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
        contacts = result
        return true
    }

    private val requestPermissionLauncher = registerForActivityResult(RequestMultiplePermissions()) {
        results: Map<String, Boolean> ->
        if (results.values.all { it }) {
            Toast.makeText(applicationContext, "Permissions granted.", Toast.LENGTH_SHORT).show()
        } else {
            showUnavailableDialog()
        }
    }

    private fun checkPermissions(): Boolean {
        val permissions = arrayOf(android.Manifest.permission.RECORD_AUDIO, android.Manifest.permission.READ_CONTACTS, android.Manifest.permission.CALL_PHONE)
        when {
            permissions.all { ActivityCompat.checkSelfPermission(applicationContext, it) == PackageManager.PERMISSION_GRANTED } -> {
                return true
            }
            permissions.any { shouldShowRequestPermissionRationale(it) } -> {
                showRationaleDialog(permissions)
            }
            else -> {
                requestPermissionLauncher.launch(permissions)
            }
        }
        return false
    }

    private fun showRationaleDialog(permissions: Array<String>) {
        val builder = AlertDialog.Builder(this)

        builder.apply {
            setMessage("Abychom vás mohli slyšet, potřebujeme přístup k mikrofonu. Abychom mohli zavolat lidem, potřebujeme přístup ke kontaktům a správě hovorů.")
            setTitle("Potřebujeme povolení!")
            setPositiveButton("OK") { _, _ ->
                requestPermissionLauncher.launch(permissions)
            }
        }
        val dialog = builder.create()
        dialog.show()
    }

    private fun showUnavailableDialog() {
        val builder = AlertDialog.Builder(this)

        builder.apply {
            setMessage("Bohužel, bez přístupu k mikrofonu, kontaktům a správě hovorů nemůžeme fungovat. Pokud chcete, přejděte do nastavení a udělte povolení.")
            setTitle("Potřebujeme povolení!")
            setPositiveButton("OK") { _, _ -> }
        }
        val dialog = builder.create()
        dialog.show()
    }
}