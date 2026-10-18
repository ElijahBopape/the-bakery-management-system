package com.bakery.app.ui

import org.junit.Assert.assertEquals
import org.junit.Test

class FormatTest {

    @Test
    fun whole_price_has_two_decimals() {
        assertEquals("R45.00", formatRand(45.0))
    }

    @Test
    fun fractional_price_keeps_cents() {
        assertEquals("R35.50", formatRand(35.5))
    }
}
