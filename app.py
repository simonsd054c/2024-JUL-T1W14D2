from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"]="postgresql+psycopg2://ecommerce_dev:123456@localhost:5432/jul_ecommerce"

db = SQLAlchemy(app)
ma = Marshmallow(app)

# Model - Table
class Product(db.Model):
    # define tablename
    __tablename__ = "products"
    # define the primary key
    id = db.Column(db.Integer, primary_key=True)
    # more attributes
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100))
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)

class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(100))

# Schema
class ProductSchema(ma.Schema):
    class Meta:
        # fields
        fields = ("id", "name", "description", "price", "stock")

class CategorySchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "description")

# to handle multiple products
products_schema = ProductSchema(many=True)
# to handle a single product
product_schema = ProductSchema()

# to handle multiple categories
categories_schema = CategorySchema(many=True)
# to handle a single category
category_schema = CategorySchema()

# CLI Commands
@app.cli.command("create")
def create_tables():
    db.create_all()
    print("Tables created")

@app.cli.command("drop")
def drop_tables():
    db.drop_all()
    print("Tables dropped")

@app.cli.command("seed")
def seed_db():
    # create a product object
    product1 = Product(
        name="Product 1",
        description="Product 1 description",
        price=12.99,
        stock=15
    )
    product2 = Product()
    product2.name = "Product 2"
    product2.price = 149.99
    product2.stock = 25
    # add to session
    db.session.add(product1)
    db.session.add(product2)

    # create list of categories object
    categories = [
        Category(
            name="Category 1",
            description="Category 1 desc"
        ),
        Category(
            name="Category 2",
            description="Category 2 desc"
        ),
        Category(
            name="Category 3"
        )
    ]
    # add the list to the session
    db.session.add_all(categories)
    # commit
    db.session.commit()
    print("Tables seeded")

# get all products - /products - GET
# get a single product - /products/id - GET
# create a product - /products - POST
# update a product - /products/id - PUT, PATCH
# delete a product - /products/id - DELETE


# CRUD for products
# R of CRUD - Read - GET
@app.route("/products")
def get_products():
    stmt = db.select(Product) # SELECT * FROM products;
    products_list = db.session.scalars(stmt)
    data = products_schema.dump(products_list)
    return data

@app.route("/products/<int:product_id>")
def get_product(product_id):
    stmt = db.select(Product).filter_by(id=product_id) # SELECT * FROM products WHERE id=product_id;
    product = db.session.scalar(stmt)
    if product:
        data = product_schema.dump(product)
        return data
    else:
        return {"message": f"Product with id {product_id} does not exist"}, 404

# C of CRUD - Create - POST
@app.route("/products", methods=["POST"])
def create_product():
    body_data = request.get_json()
    new_product = Product(
        name=body_data.get("name"),
        description=body_data.get("description"),
        price=body_data.get("price"),
        stock=body_data.get("stock")
    )
    db.session.add(new_product)
    db.session.commit()
    return product_schema.dump(new_product), 201

# D of CRUD - Delete - DELETE
@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    # find the product with that id from the db
    stmt = db.select(Product).where(Product.id==product_id) # SELECT * FROM products WHERE id=product_id;
    product = db.session.scalar(stmt)
    # if product exists
    if product:
        # delete the product
        db.session.delete(product)
        db.session.commit()
        # respond with a message saying the product has been deleted
        return {"message": f"Product '{product.name}' deleted successfully"}
    # else
    else:
        # respond with a message saying product with that id does not exist
        return {"message": f"Product with id {product_id} does not exist"}, 404

# U of CRUD - Update - PUT, PATCH
@app.route("/products/<int:product_id>", methods=["PUT", "PATCH"])
def update_product(product_id):
    # find the product with that id from the db to update
    stmt = db.select(Product).filter_by(id=product_id)
    product = db.session.scalar(stmt)
    # get the data to be updated from the body of the request
    body_data = request.get_json()
    # if product exists
    if product:
        # update the product
        product.name = body_data.get("name") or product.name
        product.description = body_data.get("description") or product.description
        product.price = body_data.get("price") or product.price
        product.stock = body_data.get("stock") or product.stock
        # commit
        db.session.commit()
        # respond accordingly
        return product_schema.dump(product)
    # else
    else:
        # respond with an error message
        return {"message": f"Product with id {product_id} does not exist"}, 404


# CRUD for categories
# Read all categories - /categories - GET
# Read a single category - /categories/id - GET
# Create category - /categories - POST
# Update category - /categories/id - PUT or PATCH
# Delete category - /categories/id - DELETE

# Read all categories
@app.route("/categories", methods=["GET"])
def get_categories():
    stmt = db.select(Category) # SELECT * FROM categories;
    categories_list = db.session.scalars(stmt)
    # convert this list of python objects into a serialisable format
    data = categories_schema.dump(categories_list)
    return data

@app.route("/categories/<int:category_id>")
def get_category(category_id):
    stmt = db.select(Category).filter_by(id=category_id) # SELECT * FROM categories WHERE id=category_id;
    category = db.session.scalar(stmt)
    if category:
        data = category_schema.dump(category)
        return data
    else:
        return {"message": f"Category with id {category_id} does not exist"}, 404

@app.route("/categories", methods=["POST"])
def create_category():
    # get the data from the body of the request
    body_data = request.get_json()
    # create a category model object using the data from the request body
    new_category = Category(
        name=body_data.get("name"),
        description=body_data.get("description")
    )
    # add it to the session
    db.session.add(new_category)
    # commit
    db.session.commit()
    # return a response
    return category_schema.dump(new_category), 201