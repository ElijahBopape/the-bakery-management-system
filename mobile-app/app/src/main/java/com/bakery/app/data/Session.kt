package com.bakery.app.data

import android.content.Context

class Session(context: Context) {

    private val prefs = context.getSharedPreferences("bakery", Context.MODE_PRIVATE)

    var token: String?
        get() = prefs.getString("token", null)
        set(value) = prefs.edit().putString("token", value).apply()

    var notificationsEnabled: Boolean
        get() = prefs.getBoolean("notifications", true)
        set(value) = prefs.edit().putBoolean("notifications", value).apply()
}
