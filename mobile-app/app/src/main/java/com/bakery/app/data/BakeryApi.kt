package com.bakery.app.data

import okhttp3.Interceptor
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

const val BAKERY_BASE_URL = "https://the-bakery-api-production.up.railway.app/"

interface BakeryApi {

    @POST("auth/register")
    suspend fun register(@Body body: UserRegister): Token

    @POST("auth/login")
    suspend fun login(@Body body: UserLogin): Token

    @GET("auth/sso")
    suspend fun sso(): UserOut

    @GET("auth/me")
    suspend fun me(): UserOut

    @GET("categories")
    suspend fun categories(): List<CategoryOut>

    @GET("products")
    suspend fun products(
        @Query("category_id") categoryId: Int?,
        @Query("available_only") availableOnly: Boolean,
    ): List<ProductOut>

    @POST("orders")
    suspend fun placeOrder(@Body body: OrderCreate): OrderOut

    @GET("orders")
    suspend fun orders(): List<OrderOut>
}

fun createBakeryApi(tokenProvider: () -> String?): BakeryApi {
    val authInterceptor = Interceptor { chain ->
        val request = chain.request()
        val token = tokenProvider()
        val authorised = if (token == null) {
            request
        } else {
            request.newBuilder().header("Authorization", "Bearer $token").build()
        }
        chain.proceed(authorised)
    }

    val client = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .build()

    return Retrofit.Builder()
        .baseUrl(BAKERY_BASE_URL)
        .client(client)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
        .create(BakeryApi::class.java)
}
