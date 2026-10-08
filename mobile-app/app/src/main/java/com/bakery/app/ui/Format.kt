package com.bakery.app.ui

import java.util.Locale

fun formatRand(price: Double): String = "R" + String.format(Locale.US, "%.2f", price)
