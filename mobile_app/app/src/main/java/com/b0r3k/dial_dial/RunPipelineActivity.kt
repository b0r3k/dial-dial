package com.b0r3k.dial_dial

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.speech.RecognizerIntent
import android.util.Log
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import androidx.appcompat.app.AppCompatActivity
import com.ibm.cloud.sdk.core.security.IamAuthenticator
import com.ibm.watson.assistant.v2.Assistant
import com.ibm.watson.assistant.v2.model.MessageInput
import com.ibm.watson.assistant.v2.model.MessageOptions
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers.IO
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import kotlinx.serialization.*
import kotlinx.serialization.json.*

class RunPipelineActivity : AppCompatActivity() {
    private var authenticator: IamAuthenticator? = null
    private var assistant: Assistant? = null
    private var sessionId: String? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        sessionId = intent.getStringExtra("EXTRA_SESSION_ID")
        authenticator = IamAuthenticator(getString(R.string.watson_assistant_apikey))
        assistant = Assistant("2021-06-22", authenticator).apply {
            serviceUrl = getString(R.string.watson_assistant_url)
        }

        val speechRecognizerIntent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "cs-CZ")
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
        }

        speechRecognitionLauncher.launch(speechRecognizerIntent)
    }

    private val speechRecognitionLauncher = registerForActivityResult(StartActivityForResult()) {
            activityResult ->
        if (activityResult.resultCode == Activity.RESULT_OK) {
            val result =
                activityResult.data?.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS)
            if (result != null && result.isNotEmpty()) {
                val textResult = result[0].toString()
                Log.i("tag", textResult)
                CoroutineScope(IO).launch {
                    getWatsonResponse(textResult)
                }
            }
        }
    }

    private suspend fun getWatsonResponse(message: String) {
        withContext(IO) {
            val messageInput = MessageInput.Builder().messageType("text").text(message).build()
            val messageOptions = MessageOptions.Builder(getString(R.string.waston_assistant_id), sessionId).input(messageInput).build()
            val response = assistant!!.message(messageOptions).execute().result
            Log.i("tag", response.output.generic[0].text().toString())
            finish()
        }
    }
}