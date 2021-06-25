package com.b0r3k.dial_dial

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.speech.RecognizerIntent
import android.util.Log
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import androidx.appcompat.app.AppCompatActivity
import com.b0r3k.dial_dial.databinding.ActivityMainBinding

class RunPipelineActivity : AppCompatActivity() {

    private var mainActBinding: ActivityMainBinding? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val speechRecognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "cs-CZ")
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)

        speechRecognitionLauncher.launch(speechRecognizerIntent)

    }

    private val speechRecognitionLauncher = registerForActivityResult(StartActivityForResult()) {
            activityResult ->
        if (activityResult.resultCode == Activity.RESULT_OK) {
            val result = activityResult.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if (result != null && result.isNotEmpty()) {
                Log.i("tag", result[0].toString())
                mainActBinding?.tvTranscript?.text = result[0].toString()
            }
        }
        finish()
    }
}