from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Welcome to Style-EZ Fashion Store"}

#data

products = [
{"id":1,"name":"Denim Jacket","brand":"Levis","category":"Jacket","price":2500,"sizes_available":["M","L","XL"],"in_stock":True},
{"id":2,"name":"Cotton T-Shirt","brand":"H&M","category":"Shirt","price":800,"sizes_available":["XS","S","M","L","XL"],"in_stock":True},
{"id":3,"name":"Formal Shirt","brand":"Zara","category":"Shirt","price":1500,"sizes_available":["S","M","L"],"in_stock":True},
{"id":4,"name":"Slim Jeans","brand":"Levis","category":"Jeans","price":2200,"sizes_available":["M","L","XL"],"in_stock":True},
{"id":5,"name":"Summer Dress","brand":"Forever21","category":"Dress","price":1800,"sizes_available":["XS","S","M"],"in_stock":False},

{"id":6,"name":"Hoodie","brand":"Adidas","category":"Jacket","price":2000,"sizes_available":["M","L","XL","XXL"],"in_stock":True},
{"id":7,"name":"Leather Jacket","brand":"Zara","category":"Jacket","price":4500,"sizes_available":["M","L","XL"],"in_stock":True},
{"id":8,"name":"Graphic T-Shirt","brand":"Nike","category":"Shirt","price":900,"sizes_available":["S","M","L","XL"],"in_stock":True},
{"id":9,"name":"Polo Shirt","brand":"Tommy Hilfiger","category":"Shirt","price":1300,"sizes_available":["M","L","XL"],"in_stock":True},
{"id":10,"name":"Cargo Pants","brand":"Puma","category":"Jeans","price":2100,"sizes_available":["M","L","XL","XXL"],"in_stock":True},

{"id":11,"name":"Chinos","brand":"Zara","category":"Jeans","price":1900,"sizes_available":["S","M","L"],"in_stock":True},
{"id":12,"name":"Mini Skirt","brand":"H&M","category":"Dress","price":1400,"sizes_available":["XS","S","M"],"in_stock":True},
{"id":13,"name":"Maxi Dress","brand":"Forever21","category":"Dress","price":2600,"sizes_available":["S","M","L"],"in_stock":False},
{"id":14,"name":"Track Pants","brand":"Nike","category":"Jeans","price":1700,"sizes_available":["M","L","XL"],"in_stock":True},
{"id":15,"name":"Sports Jacket","brand":"Adidas","category":"Jacket","price":3000,"sizes_available":["M","L","XL","XXL"],"in_stock":True},

{"id":16,"name":"Tank Top","brand":"H&M","category":"Shirt","price":600,"sizes_available":["XS","S","M","L"],"in_stock":True},
{"id":17,"name":"Flannel Shirt","brand":"Levis","category":"Shirt","price":1600,"sizes_available":["M","L","XL"],"in_stock":True},
{"id":18,"name":"Baggy Jeans","brand":"Puma","category":"Jeans","price":2300,"sizes_available":["M","L","XL","XXL","XXXL"],"in_stock":True},
{"id":19,"name":"Evening Gown","brand":"Zara","category":"Dress","price":5200,"sizes_available":["S","M","L"],"in_stock":False},
{"id":20,"name":"Oversized Hoodie","brand":"Nike","category":"Jacket","price":2100,"sizes_available":["M","L","XL","XXL","XXXL"],"in_stock":True}
]

orders = []
order_counter = 1

cart = []

#helper func

def validate_size(product, size):
    if size not in product["sizes_available"]:
        return False
    return True

def find_product(product_id):
    for p in products:
        if p["id"] == product_id:
            return p
    return None

def calculate_bill(price, quantity, gift_wrap, season_sale):

    base_price = price * quantity

    season_discount = 0
    if season_sale:
        season_discount = base_price * 0.15

    price_after_season_sale = base_price - season_discount

    gift_wrap_cost = 0
    if gift_wrap:
        gift_wrap_cost = 50 * quantity

    subtotal = price_after_season_sale + gift_wrap_cost

    bulk_discount = 0
    if quantity >= 5:
        bulk_discount = subtotal * 0.05

    final_total = subtotal - bulk_discount

    return {
        "base_price": base_price,
        "season_sale_discount": season_discount,
        "gift_wrap_cost": gift_wrap_cost,
        "bulk_discount": bulk_discount,
        "final_total": final_total
    }


def filter_products_logic(category, max_price, in_stock):
    result = []

    for p in products:
        if category is not None and p["category"].lower() != category.lower():
            continue
        if max_price is not None and p["price"] > max_price:
            continue
        if in_stock is not None and p["in_stock"] != in_stock:
            continue
        result.append(p)

    return result


#routes

@app.get("/products")
def get_products():
    in_stock_count = 0

    for product in products:
        if product["in_stock"]:
            in_stock_count += 1

    return {
        "total": len(products),
        "in_stock_count": in_stock_count,
        "products": products
    }


@app.get("/products/summary")
def summary():
    available = [p for p in products if p["in_stock"]]
    unavailable = [p for p in products if not p["in_stock"]]

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": len(products),
        "available": len(available),
        "unavailable": len(unavailable),
        "categories": categories
    }


@app.get("/products/{product_id}")
def get_product(product_id: int):
    p = find_product(product_id)

    if not p:
        return {"error": "Product not found"}

    return p


@app.get("/orders")
def get_orders():

    total_revenue = sum(order["total_price"] for order in orders)

    return {
        "total": len(orders),
        "total_revenue": total_revenue,
        "orders": orders
    }


#models

class OrderRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    size: str
    quantity: int = Field(..., gt=0, le=20)
    delivery_address: str = Field(..., min_length=10)
    gift_wrap: bool = False
    season_sale: bool = False


class NewProduct(BaseModel):
    name: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    category: str = Field(..., min_length=2)
    in_stock: bool = True


class CheckoutRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    delivery_address: str = Field(..., min_length=10)


#post order

@app.post("/orders")
def place_order(order: OrderRequest):

    global order_counter

    product = find_product(order.product_id)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": "Product unavailable"}

    bill = calculate_bill(
        product["price"],
        order.quantity,
        order.gift_wrap,
        order.season_sale
    )

    new_order = {
        "order_id": order_counter,
        "customer_name": order.customer_name,
        "product": product["name"],
        "size": order.size,
        "quantity": order.quantity,
        "total_price": bill["final_total"],
        "bill_breakdown": bill,
        "address": order.delivery_address
    }

    orders.append(new_order)
    order_counter += 1

    return new_order


#filtering

@app.get("/products/filter")
def filter_products(
    category: Optional[str] = None,
    max_price: Optional[int] = None,
    in_stock: Optional[bool] = None
):

    result = filter_products_logic(category, max_price, in_stock)

    return {"count": len(result), "products": result}


#crud

@app.post("/products")
def add_product(product: NewProduct, response: Response):

    for p in products:
        if p["name"].lower() == product.name.lower():
            return {"error": "Product already exists"}

    new_id = max(p["id"] for p in products) + 1

    item = {
        "id": new_id,
        **product.dict()
    }

    products.append(item)

    response.status_code = 201

    return item


@app.put("/products/{product_id}")
def update_product(
        product_id: int,
        price: Optional[int] = None,
    in_stock: Optional[bool] = None):

    p = find_product(product_id)

    if not p:
        return {"error": "Product not found"}

    if price is not None:
        p["price"] = price

    if in_stock is not None:
        p["in_stock"] = in_stock

    return p


@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    p = find_product(product_id)

    if not p:
        return {"error": "Product not found"}

    products.remove(p)

    return {"message": f"{p['name']} deleted"}


#cart

@app.post("/cart/add")
def add_to_cart(product_id: int, size: str, quantity: int = 1):

    product = find_product(product_id)

    if not product:
        return {"error": "Product not found"}

    if not product["in_stock"]:
        return {"error": "Product out of stock"}

    if size not in product["sizes_available"]:
        return {"error": "Selected size not available"}

    for item in cart:
        if item["product_id"] == product_id and item["size"] == size:
            item["quantity"] += quantity
            return {"message": "quantity updated", "cart": cart}

    cart.append({
        "product_id": product_id,
        "name": product["name"],
        "size": size,
        "price": product["price"],
        "quantity": quantity
    })

    return {"message": "added to cart", "cart": cart}

@app.get("/cart")
def view_cart():

    total = sum(item["price"] * item["quantity"] for item in cart)

    return {"items": cart, "grand_total": total}


@app.delete("/cart/{product_id}")
def remove_cart(product_id: int):

    for item in cart:
        if item["product_id"] == product_id:
            cart.remove(item)
            return {"message": "item removed"}

    return {"error": "item not in cart"}


@app.post("/cart/checkout")
def checkout(req: CheckoutRequest, response: Response):

    global order_counter

    if not cart:
        return {"error": "Cart empty"}

    placed_orders = []
    total = 0

    for item in cart:

        price = item["price"] * item["quantity"]

        order = {
            "order_id": order_counter,
            "customer_name": req.customer_name,
            "product": item["name"],
            "size": item["size"],
            "quantity": item["quantity"],
            "total_price": price,
            "delivery_address": req.delivery_address
        }

        orders.append(order)
        placed_orders.append(order)

        total += price
        order_counter += 1

    cart.clear()

    response.status_code = 201

    return {
        "orders": placed_orders,
        "grand_total": total
    }

#searching

@app.get("/products/search")
def search_products(keyword: str):

    results = [
        p for p in products
        if keyword.lower() in p["name"].lower()
        or keyword.lower() in p["category"].lower()
    ]

    if not results:
        return {"message": "No matching products"}

    return {"total_found": len(results), "products": results}


#sorting

@app.get("/products/sort")
def sort_products(sort_by: str = "price", order: str = "asc"):

    if sort_by not in ["price", "name", "category"]:
        return {"error": "Invalid sort field"}

    if order not in ["asc", "desc"]:
        return {"error": "Invalid order"}

    reverse = order == "desc"

    sorted_list = sorted(products, key=lambda x: x[sort_by], reverse=reverse)

    return {
        "sort_by": sort_by,
        "order": order,
        "products": sorted_list
    }


#pagination

@app.get("/products/page")
def paginate_products(
        page: int = Query(1, ge=1),
        limit: int = Query(3, ge=1, le=10)):

    start = (page - 1) * limit

    total = len(products)

    total_pages = math.ceil(total / limit)

    items = products[start:start + limit]

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "items": items
    }


#search+sort

@app.get("/orders/search")
def search_orders(customer_name: str):

    result = [
        o for o in orders
        if customer_name.lower() in o["customer_name"].lower()
    ]

    return {"count": len(result), "orders": result}


@app.get("/orders/sort")
def sort_orders(order: str = "asc"):

    reverse = order == "desc"

    sorted_list = sorted(orders, key=lambda x: x["total_price"], reverse=reverse)

    return {"orders": sorted_list}


#browse

@app.get("/products/browse")
def browse_products(
        keyword: Optional[str] = None,
        sort_by: str = "price",
        order: str = "asc",
        page: int = 1,
        limit: int = 4):

    data = products

    if keyword:
        data = [
            p for p in data
            if keyword.lower() in p["name"].lower()
            or keyword.lower() in p["category"].lower()
        ]

    reverse = order == "desc"

    data = sorted(data, key=lambda x: x[sort_by], reverse=reverse)

    total = len(data)

    start = (page - 1) * limit

    paginated = data[start:start + limit]

    total_pages = math.ceil(total / limit)

    return {
        "keyword": keyword,
        "sort_by": sort_by,
        "order": order,
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": total_pages,
        "products": paginated
    }