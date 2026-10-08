package com.bakery.app.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.automirrored.filled.List
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.ShoppingCart
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.bakery.app.AppViewModel
import com.bakery.app.SessionCheck

object Route {
    const val Splash = "splash"
    const val Login = "login"
    const val Register = "register"
    const val Home = "home"
    const val Cart = "cart"
    const val Orders = "orders"
    const val Settings = "settings"
}

@Composable
fun BakeryApp(viewModel: AppViewModel = viewModel()) {
    val navController = rememberNavController()
    val backStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = backStackEntry?.destination?.route
    val tabRoutes = setOf(Route.Home, Route.Cart, Route.Orders, Route.Settings)

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        bottomBar = {
            if (currentRoute in tabRoutes) {
                NavigationBar(containerColor = MaterialTheme.colorScheme.surface) {
                    NavigationBarItem(
                        selected = currentRoute == Route.Home,
                        onClick = { navController.navigateToTab(Route.Home) },
                        icon = { Icon(Icons.Filled.Home, contentDescription = "Menu") },
                        label = { Text("Menu") },
                    )
                    NavigationBarItem(
                        selected = currentRoute == Route.Cart,
                        onClick = { navController.navigateToTab(Route.Cart) },
                        icon = { Icon(Icons.Filled.ShoppingCart, contentDescription = "Cart") },
                        label = { Text("Cart (${viewModel.cartCount})") },
                    )
                    NavigationBarItem(
                        selected = currentRoute == Route.Orders,
                        onClick = { navController.navigateToTab(Route.Orders) },
                        icon = { Icon(Icons.AutoMirrored.Filled.List, contentDescription = "Orders") },
                        label = { Text("Orders") },
                    )
                    NavigationBarItem(
                        selected = currentRoute == Route.Settings,
                        onClick = { navController.navigateToTab(Route.Settings) },
                        icon = { Icon(Icons.Filled.Settings, contentDescription = "Settings") },
                        label = { Text("Settings") },
                    )
                }
            }
        },
    ) { innerPadding ->
        NavHost(
            navController = navController,
            startDestination = Route.Splash,
            modifier = Modifier.padding(innerPadding),
        ) {
            composable(Route.Splash) {
                SplashScreen(viewModel) { result ->
                    val next = if (result == SessionCheck.Valid || result == SessionCheck.Offline) {
                        Route.Home
                    } else {
                        Route.Login
                    }
                    navController.navigate(next) {
                        popUpTo(Route.Splash) { inclusive = true }
                    }
                }
            }
            composable(Route.Login) {
                LoginScreen(
                    viewModel = viewModel,
                    onSignedIn = { navController.openHome() },
                    onRegister = { navController.navigate(Route.Register) },
                )
            }
            composable(Route.Register) {
                RegisterScreen(
                    viewModel = viewModel,
                    onRegistered = { navController.openHome() },
                    onBack = { navController.popBackStack() },
                )
            }
            composable(Route.Home) {
                HomeScreen(viewModel)
            }
            composable(Route.Cart) {
                CartScreen(
                    viewModel = viewModel,
                    onOrdered = { navController.navigateToTab(Route.Orders) },
                )
            }
            composable(Route.Orders) {
                OrdersScreen(viewModel)
            }
            composable(Route.Settings) {
                SettingsScreen(
                    viewModel = viewModel,
                    onSignedOut = {
                        navController.navigate(Route.Login) {
                            popUpTo(navController.graph.id) { inclusive = true }
                        }
                    },
                )
            }
        }
    }
}

private fun NavHostController.navigateToTab(route: String) = navigate(route) {
    popUpTo(Route.Home) { inclusive = false }
    launchSingleTop = true
}

private fun NavHostController.openHome() = navigate(Route.Home) {
    popUpTo(graph.id) { inclusive = true }
}
