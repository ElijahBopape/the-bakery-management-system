package com.bakery.app.data

import com.google.gson.Gson
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class ModelsTest {

    private val gson = Gson()

    @Test
    fun token_parses_snake_case_fields_and_user() {
        val token = gson.fromJson(
            """{"access_token":"abc","token_type":"bearer","user":$USER_JSON}""",
            Token::class.java,
        )

        assertEquals("abc", token.accessToken)
        assertEquals("bearer", token.tokenType)
        assertEquals("Thabo", token.user.name)
        assertNull(token.user.phone)
    }

    @Test
    fun product_parses_price_and_availability() {
        val product = gson.fromJson(
            """{"id":4,"name":"Chocolate Cake","description":null,"price":180.0,
            "category_id":2,"image_url":null,"is_available":true,
            "created_at":"2026-10-05T17:54:17"}""",
            ProductOut::class.java,
        )

        assertEquals("Chocolate Cake", product.name)
        assertEquals(180.0, product.price, 0.0)
        assertEquals(2, product.categoryId)
        assertEquals(true, product.isAvailable)
    }

    @Test
    fun order_parses_items_and_total() {
        val order = gson.fromJson(
            """{"id":1,"user_id":1,"total":360.0,"status":"pending","delivery_address":"12 Main St",
            "notes":null,"created_at":"2026-10-18T10:00:00",
            "items":[{"id":1,"product_id":4,"product":null,"quantity":2,"unit_price":180.0}]}""",
            OrderOut::class.java,
        )

        assertEquals(360.0, order.total, 0.0)
        assertEquals("pending", order.status)
        assertEquals("12 Main St", order.deliveryAddress)
        assertEquals(2, order.items.orEmpty().single().quantity)
    }

    @Test
    fun order_create_serialises_to_snake_case_and_omits_nulls() {
        val json = gson.toJson(
            OrderCreate(listOf(OrderItemCreate(productId = 4, quantity = 2)), "12 Main St", null),
        )

        assertEquals(
            """{"items":[{"product_id":4,"quantity":2}],"delivery_address":"12 Main St"}""",
            json,
        )
    }

    private companion object {
        const val USER_JSON =
            """{"id":1,"name":"Thabo","email":"thabo@gmail.com","role":"customer","phone":null,"created_at":"2026-10-05T17:54:20"}"""
    }
}
