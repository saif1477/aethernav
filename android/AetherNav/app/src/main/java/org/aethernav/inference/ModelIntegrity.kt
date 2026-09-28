package org.aethernav.inference

import android.content.Context
import java.security.MessageDigest

object ModelIntegrity {
    fun sha256(context: Context, assetName: String): String = MessageDigest.getInstance("SHA-256").digest(context.assets.open(assetName).use { it.readBytes() }).joinToString("") { "%02x".format(it) }
    fun verify(context: Context, assetName: String, expected: String?): Boolean = expected != null && sha256(context, assetName).equals(expected, ignoreCase = true)
}
