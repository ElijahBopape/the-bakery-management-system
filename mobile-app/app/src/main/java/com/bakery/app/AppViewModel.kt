package com.bakery.app

import android.app.Application
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.bakery.app.data.BakeryApi
import com.bakery.app.data.CategoryOut
import com.bakery.app.data.OrderCreate
import com.bakery.app.data.OrderItemCreate
import com.bakery.app.data.OrderOut
import com.bakery.app.data.ProductOut
import com.bakery.app.data.Session
import com.bakery.app.data.Token
import com.bakery.app.data.UserLogin
import com.bakery.app.data.UserOut
import com.bakery.app.data.UserRegister
import com.bakery.app.data.createBakeryApi
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.io.IOException

enum class SessionCheck { NoToken, Valid, Rejected, Offline }

class AppViewModel(application: Application) : AndroidViewModel(application) {

    private val session = Session(application)
    private val api: BakeryApi = createBakeryApi { session.token }

    var user by mutableStateOf<UserOut?>(null)
        private set
    var categories by mutableStateOf<List<CategoryOut>>(emptyList())
        private set
    var products by mutableStateOf<List<ProductOut>>(emptyList())
        private set
    var selectedCategoryId by mutableStateOf<Int?>(null)
        private set
    var busy by mutableStateOf(false)
        private set
    var error by mutableStateOf<String?>(null)
        private set
    var notificationsEnabled by mutableStateOf(session.notificationsEnabled)
        private set
    var cart by mutableStateOf<Map<Int, Int>>(emptyMap())
        private set
    var orders by mutableStateOf<List<OrderOut>>(emptyList())
        private set

    val cartCount: Int get() = cart.values.sum()

    fun cartTotal(): Double = products.sumOf { it.price * (cart[it.id] ?: 0) }

    fun addToCart(productId: Int) {
        cart = cart + (productId to (cart[productId] ?: 0) + 1)
    }

    fun removeFromCart(productId: Int) {
        val quantity = (cart[productId] ?: 0) - 1
        cart = if (quantity <= 0) cart - productId else cart + (productId to quantity)
    }

    fun placeOrder(address: String, notes: String, onSuccess: () -> Unit) = perform(onSuccess) {
        val items = cart.map { (productId, quantity) -> OrderItemCreate(productId, quantity) }
        api.placeOrder(OrderCreate(items, address.ifBlank { null }, notes.ifBlank { null }))
        cart = emptyMap()
        orders = api.orders()
    }

    fun loadOrders() = perform {
        orders = api.orders()
    }

    suspend fun checkSession(): SessionCheck {
        if (session.token == null) return SessionCheck.NoToken
        return try {
            user = api.sso()
            SessionCheck.Valid
        } catch (e: HttpException) {
            if (e.code() == 401 || e.code() == 403) {
                session.token = null
                SessionCheck.Rejected
            } else {
                SessionCheck.Offline
            }
        } catch (e: IOException) {
            SessionCheck.Offline
        }
    }

    fun login(email: String, password: String, onSuccess: () -> Unit) = perform(onSuccess) {
        store(api.login(UserLogin(email, password)))
    }

    fun register(name: String, email: String, password: String, phone: String, onSuccess: () -> Unit) =
        perform(onSuccess) {
            store(api.register(UserRegister(name, email, password, phone.ifBlank { null })))
        }

    fun loadMenu() = perform {
        categories = api.categories()
        products = api.products(selectedCategoryId, availableOnly = true)
    }

    fun selectCategory(categoryId: Int?) {
        selectedCategoryId = categoryId
        loadMenu()
    }

    fun loadProfile() = perform {
        user = api.me()
    }

    fun logout(onSuccess: () -> Unit) {
        session.token = null
        user = null
        categories = emptyList()
        products = emptyList()
        selectedCategoryId = null
        cart = emptyMap()
        orders = emptyList()
        onSuccess()
    }

    fun toggleNotifications(enabled: Boolean) {
        notificationsEnabled = enabled
        session.notificationsEnabled = enabled
    }

    fun clearError() {
        error = null
    }

    private fun store(token: Token) {
        session.token = token.accessToken
        user = token.user
    }

    private fun perform(onSuccess: () -> Unit = {}, block: suspend () -> Unit) {
        viewModelScope.launch {
            busy = true
            error = null
            try {
                block()
                onSuccess()
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                error = describe(e)
            } finally {
                busy = false
            }
        }
    }

    private fun describe(e: Exception): String = when (e) {
        is HttpException -> {
            val detail = e.response()?.errorBody()?.string()
                ?.let { Regex("\"detail\"\\s*:\\s*\"([^\"]+)\"").find(it)?.groupValues?.get(1) }
            detail ?: if (e.code() == 401) "Invalid email or password" else "Server error (${e.code()})"
        }
        is IOException -> "Can't reach the server. Check your connection."
        else -> e.message ?: "Something went wrong."
    }
}
