package com.bakery.app.ui

import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Shapes
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

private val BakeryColors = darkColorScheme(
    primary = Color(0xFFE6AC3D),
    onPrimary = Color(0xFF1A1410),
    primaryContainer = Color(0xFF2A241F),
    onPrimaryContainer = Color(0xFFE6AC3D),
    secondary = Color(0xFFC08F2E),
    onSecondary = Color(0xFF1A1410),
    secondaryContainer = Color(0xFF3A2C14),
    onSecondaryContainer = Color(0xFFF0CC83),
    background = Color(0xFF0A0807),
    onBackground = Color(0xFFECE4D6),
    surface = Color(0xFF1A1613),
    onSurface = Color(0xFFECE4D6),
    surfaceVariant = Color(0xFF2A241F),
    onSurfaceVariant = Color(0xFFA89A86),
    surfaceContainerLowest = Color(0xFF0A0807),
    surfaceContainerLow = Color(0xFF140F0C),
    surfaceContainer = Color(0xFF1A1613),
    surfaceContainerHigh = Color(0xFF221D18),
    surfaceContainerHighest = Color(0xFF2A241F),
    outline = Color(0xFF4A3F30),
    outlineVariant = Color(0xFF4A3F30),
    error = Color(0xFFE06A52),
    onError = Color(0xFF1A1410),
)

private val BakeryTypography = Typography(
    headlineLarge = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Bold,
        fontSize = 34.sp,
        lineHeight = 40.sp,
    ),
    headlineMedium = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        lineHeight = 34.sp,
    ),
    titleLarge = TextStyle(
        fontFamily = FontFamily.Serif,
        fontWeight = FontWeight.Bold,
        fontSize = 20.sp,
        lineHeight = 26.sp,
    ),
)

private val BakeryShapes = Shapes(
    small = RoundedCornerShape(8.dp),
    medium = RoundedCornerShape(12.dp),
    large = RoundedCornerShape(12.dp),
)

@Composable
fun BakeryTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = BakeryColors,
        typography = BakeryTypography,
        shapes = BakeryShapes,
        content = content,
    )
}
