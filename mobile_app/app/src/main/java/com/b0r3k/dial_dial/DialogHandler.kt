package com.b0r3k.dial_dial

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import com.b0r3k.dial_dial.databinding.ActivityMainBinding


class DialogHandler (context: Context, private val binding: ActivityMainBinding) {
    private val speechRecognizer = SpeechRecognizer.createSpeechRecognizer(context)
    private val speechRecognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH)
    init {
        speechRecognizerIntent.putExtra(
            RecognizerIntent.EXTRA_LANGUAGE_MODEL,
            RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
        )
        speechRecognizerIntent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "cs-CZ")
    }

    fun process() {
        this.getSpeech()
    }

    private fun getSpeech() {
        speechRecognizer.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(bundle: Bundle) {}
            override fun onBeginningOfSpeech() {
                binding.tvTranscript.text = "Listening..."
            }

            override fun onRmsChanged(v: Float) {}
            override fun onBufferReceived(bytes: ByteArray) {}
            override fun onEndOfSpeech() {}
            override fun onError(i: Int) {}
            override fun onResults(bundle: Bundle) {
                binding.ivSpeak.setImageResource(R.drawable.ic_mic_empty)
                val data = bundle.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                binding.tvTranscript.text = data!![0]
            }

            override fun onPartialResults(bundle: Bundle) {}
            override fun onEvent(i: Int, bundle: Bundle) {}
        })

    }
}