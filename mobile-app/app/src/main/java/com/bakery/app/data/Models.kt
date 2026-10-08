package com.bakery.app.data

import com.google.gson.annotations.SerializedName

data class UserOut(
    val id: Int,
    val name: String,
    val email: String,
    val role: String,
    val phone: String?,
    @SerializedName("created_at") val createdAt: String?,
)

data class Token(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String,
    val user: UserOut,
)

data class UserLogin(
    val email: String,
    val password: String,
)

data class UserRegister(
    val name: String,
    val email: String,
    val password: String,
    val phone: String?,
)

data class CategoryOut(
    val id: Int,
    val name: String,
    val description: String?,
)

data class ProductOut(
    val id: Int,
    val name: String,
    val description: String?,
    val price: Double,
    @SerializedName("category_id") val categoryId: Int,
    @SerializedName("image_url") val imageUrl: String?,
    @SerializedName("is_available") val isAvailable: Boolean,
)

data class OrderItemCreate(
    @SerializedName("product_id") val productId: Int,
    val quantity: Int,
)

data class OrderCreate(
    val items: List<OrderItemCreate>,
    @SerializedName("delivery_address") val deliveryAddress: String?,
    val notes: String?,
)

data class OrderItemOut(
    val id: Int,
    @SerializedName("product_id") val productId: Int,
    val product: ProductOut?,
    val quantity: Int,
    @SerializedName("unit_price") val unitPrice: Double,
)

data class OrderOut(
    val id: Int,
    @SerializedName("user_id") val userId: Int,
    val total: Double,
    val status: String,
    @SerializedName("delivery_address") val deliveryAddress: String?,
    val notes: String?,
    @SerializedName("created_at") val createdAt: String,
    val items: List<OrderItemOut>?,
)
