from flask import Flask, render_template_string

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Distributor App</title>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            margin: 0;
            background: #f4f4f4;
            color: #222;
        }

        header {
            background: #d71920;
            color: white;
            text-align: center;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 20px auto;
            padding: 15px;
        }

        .card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        h2 {
            margin-top: 0;
        }

        input, select {
            width: 100%;
            padding: 12px;
            margin: 8px 0 15px;
            border: 1px solid #ccc;
            border-radius: 8px;
            font-size: 16px;
        }

        button {
            background: #d71920;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }

        button:hover {
            background: #b51218;
        }

        .add-btn {
            background: #222;
        }

        .order-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f7f7f7;
            padding: 12px;
            margin-top: 10px;
            border-radius: 8px;
        }

        .delete-btn {
            background: #777;
            padding: 8px 12px;
            margin: 0;
        }

        .total {
            font-size: 24px;
            font-weight: bold;
            color: #d71920;
        }

        .row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }

        @media (max-width: 600px) {
            .row {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>

<body>

<header>
    <h1>Distributor App</h1>
    <p>Order & Case Price Calculator</p>
</header>

<div class="container">

    <div class="card">
        <h2>Customer Details</h2>

        <input type="text" id="customerName" placeholder="Customer Name">

        <input type="text" id="shopName" placeholder="Shop Name">

        <input type="text" id="phone" placeholder="Phone Number">
    </div>


    <div class="card">
        <h2>Add Product</h2>

        <label>Product</label>

        <select id="product" onchange="setRate()">
            <option value="Coca-Cola">Coca-Cola</option>
            <option value="Sprite">Sprite</option>
            <option value="Fanta">Fanta</option>
            <option value="Thums Up">Thums Up</option>
            <option value="Maaza">Maaza</option>
        </select>

        <div class="row">

            <div>
                <label>Rate Per Case (₹)</label>
                <input type="number" id="rate" value="500">
            </div>

            <div>
                <label>Number of Cases</label>
                <input type="number" id="quantity" value="1" min="1">
            </div>

        </div>

        <button class="add-btn" onclick="addProduct()">
            Add Product
        </button>

    </div>


    <div class="card">

        <h2>Order Items</h2>

        <div id="orderItems">
            No products added.
        </div>

    </div>


    <div class="card">

        <h2>Order Summary</h2>

        <label>Discount (₹)</label>

        <input
            type="number"
            id="discount"
            value="0"
            min="0"
            oninput="calculateTotal()"
        >

        <p>
            Subtotal:
            <strong>₹<span id="subtotal">0</span></strong>
        </p>

        <p>
            Discount:
            <strong>₹<span id="discountDisplay">0</span></strong>
        </p>

        <hr>

        <p class="total">
            Final Total: ₹<span id="finalTotal">0</span>
        </p>

        <button onclick="generateOrder()">
            Generate Order
        </button>

    </div>


    <div class="card" id="invoice" style="display:none;">

        <h2>Order Invoice</h2>

        <p>
            <strong>Customer:</strong>
            <span id="invoiceCustomer"></span>
        </p>

        <p>
            <strong>Shop:</strong>
            <span id="invoiceShop"></span>
        </p>

        <p>
            <strong>Phone:</strong>
            <span id="invoicePhone"></span>
        </p>

        <hr>

        <div id="invoiceItems"></div>

        <hr>

        <h2>
            Total: ₹<span id="invoiceTotal"></span>
        </h2>

        <button onclick="window.print()">
            Print Invoice
        </button>

    </div>

</div>


<script>

let products = {

    "Coca-Cola": 500,
    "Sprite": 480,
    "Fanta": 470,
    "Thums Up": 500,
    "Maaza": 450

};


let order = [];


function setRate() {

    let product =
        document.getElementById("product").value;

    document.getElementById("rate").value =
        products[product];

}


function addProduct() {

    let product =
        document.getElementById("product").value;

    let rate =
        Number(document.getElementById("rate").value);

    let quantity =
        Number(document.getElementById("quantity").value);


    if (quantity <= 0 || rate < 0) {

        alert("Please enter valid values.");

        return;

    }


    let total =
        rate * quantity;


    order.push({

        product: product,
        rate: rate,
        quantity: quantity,
        total: total

    });


    displayOrder();

    calculateTotal();

}


function displayOrder() {

    let container =
        document.getElementById("orderItems");


    if (order.length === 0) {

        container.innerHTML =
            "No products added.";

        return;

    }


    container.innerHTML = "";


    order.forEach(function(item, index) {

        container.innerHTML += `

        <div class="order-item">

            <div>

                <strong>${item.product}</strong>

                <br>

                ${item.quantity} Cases × ₹${item.rate}

                = ₹${item.total}

            </div>


            <button
                class="delete-btn"
                onclick="removeProduct(${index})">

                Remove

            </button>

        </div>

        `;

    });

}


function removeProduct(index) {

    order.splice(index, 1);

    displayOrder();

    calculateTotal();

}


function calculateTotal() {

    let subtotal = 0;


    order.forEach(function(item) {

        subtotal += item.total;

    });


    let discount =
        Number(
            document.getElementById("discount").value
        );


    let finalTotal =
        subtotal - discount;


    if (finalTotal < 0) {

        finalTotal = 0;

    }


    document.getElementById("subtotal")
        .innerText = subtotal;


    document.getElementById("discountDisplay")
        .innerText = discount;


    document.getElementById("finalTotal")
        .innerText = finalTotal;

}


function generateOrder() {

    if (order.length === 0) {

        alert("Please add at least one product.");

        return;

    }


    document.getElementById("invoice")
        .style.display = "block";


    document.getElementById("invoiceCustomer")
        .innerText =
        document.getElementById("customerName").value;


    document.getElementById("invoiceShop")
        .innerText =
        document.getElementById("shopName").value;


    document.getElementById("invoicePhone")
        .innerText =
        document.getElementById("phone").value;


    let invoiceItems =
        document.getElementById("invoiceItems");


    invoiceItems.innerHTML = "";


    order.forEach(function(item) {

        invoiceItems.innerHTML += `

        <p>

            <strong>${item.product}</strong>

            <br>

            ${item.quantity} Cases × ₹${item.rate}

            = ₹${item.total}

        </p>

        `;

    });


    document.getElementById("invoiceTotal")
        .innerText =
        document.getElementById("finalTotal").innerText;

}

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(debug=True)
