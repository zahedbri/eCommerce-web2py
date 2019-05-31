# -*- coding: utf-8 -*-
db.define_table('products',
                Field('productName','text',unique=True,requires=IS_LENGTH(40,6)),
                Field('productDescription','text',requires=IS_LENGTH(450,6)),
                Field('productImage','upload',unique = True,uploadseparate=True,autodelete=True,requires=([IS_IMAGE(extensions=('jpeg', 'png')),IS_LENGTH(3145728, 1024)])),
                Field('productImage2','upload',unique = True,uploadseparate=True,autodelete=True,requires=IS_EMPTY_OR([IS_IMAGE(extensions=('jpeg', 'png')),IS_LENGTH(3145728, 1024)])),
                Field('productPrice','float',requires=[IS_DECIMAL_IN_RANGE(0.01, 1000.00,dot='.'),IS_NOT_EMPTY()]),
                Field('productQuantity','integer',requires=IS_INT_IN_RANGE(0, 10000)),
                Field('productSize','text', requires=IS_IN_SET(["XS","S","M","L","XL"])),
                Field('productType','text',requires=IS_IN_SET(["Jeans", "Chinos", "Trousers", "Sweatpants", "Shorts", "TShirts", "Shirts", "Hoodies", "Sweatshirts", "Jackets","Suits"])),
                Field('productAvgRating','float',requires=IS_DECIMAL_IN_RANGE(0.00, 5.00, dot='.'))
               )

db.define_table('product_reviews',
                 Field('reviewsTitle','text',requires=IS_LENGTH(64,4)),
                 Field('reviewsRating','integer',requires=IS_IN_SET(range(1, 6))),
                 Field('reviewsText','text',requires=IS_LENGTH(256,6)),
                 Field('productID','reference products','integer',requires=IS_NOT_EMPTY()),
                 auth.signature
               )
#To clear tables if needed
#db.products.truncate()
#db.product_reviews.truncate()
#db.auth_user.truncate()
#db.auth_group.truncate()
#db.auth_membership.truncate()
