package com.b0r3k.dial_dial

import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import com.b0r3k.dial_dial.databinding.ActivityMainBinding
import androidx.activity.result.contract.ActivityResultContracts.RequestMultiplePermissions
import androidx.appcompat.app.AlertDialog


class MainActivity : AppCompatActivity() {

    private val requestPermissionLauncher =
        registerForActivityResult(RequestMultiplePermissions()
        ) { results: Map<String, Boolean> ->
            if (results.values.all { it }) {
                Toast.makeText(applicationContext, "Permissions granted.", Toast.LENGTH_SHORT).show()
            } else {
                showUnavailableDialog()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val mainActBinding = ActivityMainBinding.inflate(layoutInflater)

        mainActBinding.ivSpeak.setOnClickListener {
            if (checkPermissions()) {
                mainActBinding.ivSpeak.setImageResource(R.drawable.ic_mic_full_red)
                DialogHandler(this, mainActBinding).process()
            }
        }
        setContentView(mainActBinding.root)
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