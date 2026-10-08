package com.bakery.app.ui

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.bakery.app.AppViewModel
import com.bakery.app.data.OrderOut

@Composable
fun OrdersScreen(viewModel: AppViewModel, modifier: Modifier = Modifier) {
    LaunchedEffect(Unit) { viewModel.loadOrders() }

    LazyColumn(
        modifier = modifier.fillMaxSize(),
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        item {
            Text("Your orders", style = MaterialTheme.typography.headlineMedium)
        }
        viewModel.error?.let { message ->
            item { ErrorText(message) }
        }
        if (viewModel.busy) {
            item {
                CircularProgressIndicator(color = MaterialTheme.colorScheme.primary)
            }
        }
        items(viewModel.orders, key = { it.id }) { order ->
            OrderCard(order)
        }
        if (!viewModel.busy && viewModel.error == null && viewModel.orders.isEmpty()) {
            item {
                Text(
                    text = "No orders yet.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
    }
}

@Composable
private fun OrderCard(order: OrderOut) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outline),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Text("Order #${order.id}", style = MaterialTheme.typography.titleLarge)
                Text(
                    text = order.status.replaceFirstChar { it.uppercase() },
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.primary,
                )
            }
            Text(
                text = order.createdAt.replace('T', ' ').take(16),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            order.items.orEmpty().forEach { item ->
                Text(
                    text = "${item.quantity} x ${item.product?.name ?: "Item #${item.productId}"}",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            Text(
                text = "Total ${formatRand(order.total)}",
                style = MaterialTheme.typography.titleMedium,
            )
        }
    }
}
