package com.b0r3k.dial_dial

import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognizerIntent
import android.util.Log
import android.widget.Toast
import androidx.activity.result.ActivityResultLauncher
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.b0r3k.dial_dial.databinding.ActivityMainBinding
import androidx.activity.result.contract.ActivityResultContracts.RequestMultiplePermissions
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import androidx.appcompat.app.AlertDialog
import com.ibm.cloud.sdk.core.security.IamAuthenticator
import com.ibm.watson.assistant.v2.Assistant
import com.ibm.watson.assistant.v2.model.CreateSessionOptions
import kotlinx.coroutines.*
import kotlinx.coroutines.Dispatchers.IO
import kotlinx.coroutines.Dispatchers.Main
import kotlinx.serialization.*
import kotlinx.serialization.json.*
import kotlin.coroutines.coroutineContext


class MainActivity : AppCompatActivity() {

    private var mainActBinding: ActivityMainBinding? = null
    private var runPipelineActivityIntent: Intent? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        mainActBinding = ActivityMainBinding.inflate(layoutInflater)

        mainActBinding?.ivCircle?.setOnClickListener {
            if (checkPermissions()) {
                CoroutineScope(IO).launch {
                    preparePipeline()
                    launchRunPipelineActivityOnMainThread()
                }
            }
        }
        setContentView(mainActBinding?.root)
    }

    private suspend fun preparePipeline() {
        withContext(IO) {
            val authenticator = IamAuthenticator(getString(R.string.watson_assistant_apikey))
            val assistant: Assistant = Assistant("2021-06-22", authenticator).apply {
                serviceUrl = getString(R.string.watson_assistant_url)
            }
            val options =
                CreateSessionOptions.Builder(getString(R.string.waston_assistant_id)).build()
            val response = assistant.createSession(options).execute().result
            val sessionId = response.sessionId

            val speechRecognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(
                    RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                    RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
                )
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, "cs-CZ")
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            }

            runPipelineActivityIntent = Intent(applicationContext, RunPipelineActivity::class.java).apply {
                //putExtra("EXTRA_ASSISTANT", Json.encodeToString(assistant))
                putExtra("EXTRA_SESSION_ID", sessionId)
                //putExtra("EXTRA_RECOGNIZER", Json.encodeToString(speechRecognizerIntent))
            }
        }
    }

    private val runPipelineActivityLauncher: ActivityResultLauncher<Intent> = registerForActivityResult(StartActivityForResult()) {
            it ->
        CoroutineScope(Main).launch {
            mainActBinding?.ivSpeak?.setImageResource(R.drawable.ic_mic_empty)
            launchRunPipelineActivityOnMainThread()
        }
    }

    private suspend fun launchRunPipelineActivityOnMainThread() {
        withContext(Main) {
            mainActBinding?.ivSpeak?.setImageResource(R.drawable.ic_mic_full_red)
            runPipelineActivityLauncher.launch(runPipelineActivityIntent)
        }
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