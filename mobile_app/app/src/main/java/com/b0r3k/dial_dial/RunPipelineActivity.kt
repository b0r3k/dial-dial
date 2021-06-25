package com.b0r3k.dial_dial

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.speech.RecognizerIntent
import android.util.Log
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import androidx.appcompat.app.AppCompatActivity
import com.ibm.watson.assistant.v2.Assistant
import kotlinx.serialization.*
import kotlinx.serialization.json.*

class RunPipelineActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val speechRecognizerIntent = Json.decodeFromString<Intent>(intent.getStringExtra("EXTRA_RECOGNIZER")!!)
        val assistant = Json.decodeFromString<Assistant>(intent.getStringExtra("EXTRA_ASSISTANT")!!)
        val sessionId = intent.getStringExtra("EXTRA_SESSION_ID")

        speechRecognitionLauncher.launch(speechRecognizerIntent)

    }

    private val speechRecognitionLauncher = registerForActivityResult(StartActivityForResult()) {
            activityResult ->
        if (activityResult.resultCode == Activity.RESULT_OK) {
            val result = activityResult.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if (result != null && result.isNotEmpty()) {
                Log.i("tag", result[0].toString())
            }
        }
        finish()
    }
}