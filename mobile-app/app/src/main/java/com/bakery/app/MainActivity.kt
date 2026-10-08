package com.bakery.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import com.bakery.app.ui.BakeryApp
import com.bakery.app.ui.BakeryTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BakeryTheme {
                BakeryApp()
            }
        }
    }
}
