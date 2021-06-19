package com.b0r3k.dial_dial

import android.app.Activity
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognizerIntent
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.b0r3k.dial_dial.databinding.ActivityMainBinding
import androidx.activity.result.contract.ActivityResultContracts.RequestMultiplePermissions
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import androidx.appcompat.app.AlertDialog


class MainActivity : AppCompatActivity() {

    private val SPEECH_REC: Int = 101
    private var mainActBinding: ActivityMainBinding? = null



    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val mainActBinding = ActivityMainBinding.inflate(layoutInflater)
        val speechRecognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "cs-CZ")

        mainActBinding.ivSpeak.setOnClickListener {
            if (checkPermissions()) {
                mainActBinding.ivSpeak.setImageResource(R.drawable.ic_mic_full_red)
                requestSpeechRecognition.launch(speechRecognizerIntent)
            }
        }
        setContentView(mainActBinding.root)
    }

    private val requestPermissionLauncher = registerForActivityResult(RequestMultiplePermissions()) {
            results: Map<String, Boolean> ->
        if (results.values.all { it }) {
            Toast.makeText(applicationContext, "Permissions granted.", Toast.LENGTH_SHORT).show()
        } else {
            showUnavailableDialog()
        }
    }

    private val requestSpeechRecognition = registerForActivityResult(StartActivityForResult()) {
            activityResult ->
        if (activityResult.resultCode == SPEECH_REC) {
            val result = activityResult.data?.getStringArrayExtra(RecognizerIntent.EXTRA_RESULTS)
            Toast.makeText(applicationContext, result.toString(), Toast.LENGTH_SHORT).show()
            if (result!!.isNotEmpty()) {
                mainActBinding!!.ivSpeak.setImageResource(R.drawable.ic_mic_empty)
                mainActBinding!!.tvTranscript.text = result.toString()
            }
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