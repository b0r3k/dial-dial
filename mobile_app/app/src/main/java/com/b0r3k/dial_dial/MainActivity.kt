package com.b0r3k.dial_dial

import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.b0r3k.dial_dial.databinding.ActivityMainBinding
import androidx.activity.result.contract.ActivityResultContracts.RequestMultiplePermissions
import androidx.activity.result.contract.ActivityResultContracts.StartActivityForResult
import androidx.appcompat.app.AlertDialog


class MainActivity : AppCompatActivity() {

    private var mainActBinding: ActivityMainBinding? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        mainActBinding = ActivityMainBinding.inflate(layoutInflater)

        mainActBinding?.ivCircle?.setOnClickListener {
            if (checkPermissions()) {
                val runPipelineActivityIntent = Intent(this, RunPipelineActivity::class.java)
                mainActBinding?.ivSpeak?.setImageResource(R.drawable.ic_mic_full_red)
                runPipelineActivityLauncher.launch(runPipelineActivityIntent)
            }
        }
        setContentView(mainActBinding?.root)
    }

    private val runPipelineActivityLauncher = registerForActivityResult(StartActivityForResult()) {
        it ->
        mainActBinding?.ivSpeak?.setImageResource(R.drawable.ic_mic_empty)
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