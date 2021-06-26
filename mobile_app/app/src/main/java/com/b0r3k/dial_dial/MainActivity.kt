package com.b0r3k.dial_dial

import android.app.Activity
import android.content.ContentResolver
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.provider.ContactsContract.CommonDataKinds.Phone
import android.speech.RecognizerIntent
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
import com.ibm.watson.assistant.v2.model.CreateSessionOptions
import com.ibm.watson.assistant.v2.model.MessageInput
import com.ibm.watson.assistant.v2.model.MessageOptions
import kotlinx.coroutines.*
import kotlinx.coroutines.Dispatchers.IO
import kotlinx.coroutines.Dispatchers.Main
import kotlinx.serialization.*
import kotlinx.serialization.json.*


class MainActivity : AppCompatActivity() {
    private var mainActBinding: ActivityMainBinding? = null
    private var sessionId : String? = null
    private var assistant: Assistant? = null
    private var speechRecognizerIntent: Intent? = null
    private var watsonReadyDeferred: Deferred<Boolean>? = null
    private var watsonReady: Boolean? = null
    private var contacts: Map<String, String>? = null

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

        mainActBinding?.ivCircle?.setOnClickListener {
            if (checkPermissions()) {
                // If not ready, prepare watson
                if ((watsonReady == null) or (watsonReady == false)) {
                    watsonReadyDeferred = CoroutineScope(IO).async {
                        loadContacts()
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
                        response = "Bohužel, nepodařilo se nám kontaktovat server."
                    }
                    delay(3000)
                    withContext(Main) {
                        Log.i("tag", response)
                        launchPipeline()
                    }
                }
            }
        }
    }

    private fun getWatsonResponse(message: String): String {
        val messageInput = MessageInput.Builder().messageType("text").text(message).build()
        val messageOptions = MessageOptions.Builder(getString(R.string.waston_assistant_id), sessionId).input(messageInput).build()
        val response = assistant!!.message(messageOptions).execute().result
        return response.output.generic[0].text().toString()
    }

    private suspend fun tryPrepareWatson(): Boolean {
        try {
            val contactsReadyDeferred = CoroutineScope(IO).async {
                return@async loadContacts()
            }
            val authenticator =
                IamAuthenticator(getString(R.string.watson_assistant_apikey))
            assistant = Assistant("2021-06-22", authenticator).apply {
                serviceUrl = getString(R.string.watson_assistant_url)
            }
            val options =
                CreateSessionOptions.Builder(getString(R.string.waston_assistant_id))
                    .build()
            val response = assistant!!.createSession(options).execute().result
            sessionId = response.sessionId
            val contactsReady = contactsReadyDeferred.await()
            if (contactsReady) {
                getWatsonResponse(Json.encodeToString(mapOf("__contacts__" to contacts!!.keys)))
            }
        } catch (e: Exception) {
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
            /*Data._ID,
            // The primary display name
            Data.DISPLAY_NAME_PRIMARY,
            // The contact's _ID, to construct a content URI*/
            Phone.NUMBER
        )
        /* val SELECTION: String = "${Data.MIMETYPE} = '${CommonDataKinds.Phone.CONTENT_ITEM_TYPE}' AND "+
                "${Data.IS_PRIMARY} != 0" */
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