import math
from gluon.tools import Recaptcha2

#Function which will update the average rating score for each product in the products table.
def updateAvG():
    products = db(db.products).select()
    for product in products:
        # Gets total number of reviews for a product
        reviewNumber=db(db.product_reviews.productID == product).count() 
        # Gets sum of all ratings for a product
        total = db(db.product_reviews.productID == product).select(db.product_reviews.reviewsRating.sum()).first()[db.product_reviews.reviewsRating.sum()]
        if (total>0):
             # Calculates average then inserts into products table.
            avgScoreReviews= (float(total)/reviewNumber)
            db(db.products.id == product).update(productAvgRating="{0:.2f}".format(avgScoreReviews))
        else:
            #If there are no reviews on a product then average will always be 0.
            db(db.products.id == product).update(productAvgRating=0)

def index():
    #gets the top 8 products
    top8 = db(db.products.id).select(orderby='products.productAvgRating DESC',limitby=(0,8))
    return locals()

@auth.requires_membership("admins")
def list_users():
    #Creates view button on the sqlform.grid
    links = [lambda row:A(SPAN(_class='icon magnifier icon-zoom-in glyphicon glyphicon-zoom-in'),' View',_class='button btn btn-default',_href=URL("manage_user",  args=row.id))]
    #Generates table
    form = SQLFORM.grid(db.auth_user,details=False,links=links,user_signature=False,editable=False,deletable=False,create=False)
    return locals()

@auth.requires_membership("admins")
def manage_user():
    #Gets user details based on URL
    user_id = request.args(0) or redirect(URL('list_users'))
    #Disables editting to certain fields
    db.auth_user.first_name.writable=False
    db.auth_user.last_name.writable=False
    db.auth_user.email.writable=False
    db.auth_user.password.writable=False
    form = SQLFORM(db.auth_user, user_id).process()
    
    #Remove the submit button for user detail form (since no edits can be done)
    submit = form.element('input',_type='submit')
    submit['_style']='display:none;'
    
    #Gets user "group" information
    #Removes information already provided in user details form
    db.auth_membership.user_id.readable = False
    db.auth_membership.user_id.writable = False
    db.auth_membership.id.readable = False
    membership_panel = SQLFORM(db.auth_membership, user_id).process() 

    bckButton = A(SPAN(_class='icon leftarrow icon-arrow-left glyphicon glyphicon-arrow-left'),' Back',_class='button btn btn-default',_href=URL("/list_users"))
    
    #User can not edit the account that they are aleady on
    if (auth.user.id==int(user_id)):
        membership_panel2=membership_panel.element('input',_type='submit')
        membership_panel2['_class']= 'button btn btn-default disabled'
        membership_panel2['_disabled']=True
        response.flash = 'Sorry you cannot edit your own account!'
            
    return dict(form=form,membership_panel=membership_panel, bckButton=bckButton)
            
def products():
    # Get information from URL
    rSearch = request.vars['searchQuery']
    rType = request.vars['type']
    rSortBy = request.vars['sortBy']
    rOrderBy = request.vars['orderBy']
    rSize = request.vars['size']
    
    #Makes sure the page number a integer & included.
    try:
        float(request.vars['page']).is_integer()
    except:
        redirect(URL(vars={'page':1,'searchQuery':rSearch,'type':rType,'sortBy':rSortBy,'orderBy':rOrderBy,'size':rSize}))

    # Converts the page into an integer instead of string, so incrementations can be done on it.
    rPage = int(request.vars['page'])

    #Default query to show all products.
    query = db.products.id
    # To be used in the pagination calculation & title's amount of found.
    count = db(query).count()
    # To be displayed on the page.
    title="Men's Clothing"

    #Different queries depending on the search or filter settings
    #Search query
    if rSearch and (rSearch!="None"):
        query = db.products.productName.contains(rSearch) | db.products.productDescription.contains(rSearch) | db.products.productType.contains(rSearch)
        count = db(query).count()
        title=("%s items found for '%s'" % (count,rSearch.capitalize()))
    #Type query
    if  rType and (rType!="None"):
        query = query & db.products.productType.startswith(rType)
        count = db(query).count()
        if rSize and (rSize!="None"):
            title = ("Men's %s - %s - %s items found" % (rType.capitalize(),rSize,count))
        else:
            title = ("Men's %s - %s items found" % (rType.capitalize(),count))
    #Size query
    if  rSize and (rSize!="None"):
        query = query & db.products.productSize.startswith(rSize)
        count = db(query).count()
        if  rType and (rType!="None"):
            title = ("Men's Size: %s - %s items found" % (rType.capitalize(),rSize,count))
        else:
            title = ("Men's Size: %s - %s items found" % (rSize,count))
    #Sort query
    if  rSortBy and (rSortBy=="price" or rSortBy=="AvgRating" or rSortBy=="Name"): # if the user edits the url and put in a sortby method which is not accepted, then no sort will be done.
        orderb=("products.product%s" %rSortBy)
    else:
        orderb="products.id"
    #Order query
    if rOrderBy=="desc":
        orderb=orderb + " DESC"
    #Sets the title if a search was done. Overrides all other titles.
    if rSearch and (rSearch!="None"):
        if (rSize!="None") and (rType!="None"):
            title=("%s items found for '%s' with type %s with size %s" % (count,rSearch.capitalize(),rType.capitalize(),rSize))
        elif rType and (rType!="None"):
            title=("%s items found for '%s' with type %s" % (count,rSearch.capitalize(),rType.capitalize()))
        elif rSize and (rSize!="None"):
            title=("%s items found for '%s' with size %s" % (count,rSearch.capitalize(),rSize))

    #Gets all the different types which will be listed in the filter types setting
    getTypes = db().select(db.products.productType,distinct=True)

    #Pagination
    pagelimit=12.0
    start = (rPage-1)*pagelimit
    end = rPage*pagelimit
    totalPages = int(math.ceil(count/pagelimit))

    #Makes sure the page number is not negative or higher than the amount of pages that there actually are
    if (rPage<=0) or ((totalPages<rPage) and (totalPages!=0)):
        redirect(URL(vars={'page':1,'searchQuery':rSearch,'type':rType,'sortBy':rSortBy,'orderBy':rOrderBy,'size':rSize}))

    #Updates average for each product then runs the query based on the search/filter settings
    updateAvG()
    products = db(query).select(orderby=orderb,limitby=(start,end))
    return locals()

def viewProduct():
    #Makes sure the item variable is an integer
    try:
        float(request.vars['item']).is_integer()
    except:
        redirect(URL(vars={'item':1}))
    
    item = int(request.vars.item)

    products = db(db.products.id == request.vars.item).select()
    #Initializes Auth
    auth.basic()
    
    #If user is logged in, enable creation of reviews
    if auth.user:
        #Sets time and productID (foreign key)
        db.product_reviews.created_on.default = request.now
        db.product_reviews.productID.default = request.vars.item
        db.product_reviews.productID.readable=False
        db.product_reviews.productID.writable=False
        form = SQLFORM(db.product_reviews,labels={'reviewsTitle':'Title','reviewsRating':'Star Rating:','reviewsText':'Description:'}).process()
        
        #Delete function will only work if the user is an admin
        if auth.has_membership(group_id='2'):
            if request.vars.delete:
                   db(db.product_reviews.id ==  request.vars.delete).delete()
                   redirect(URL(vars={'item':item}))

    #Recalculates star average for product again after review delete/creation
    updateAvG()
    
    #Gets type of the products
    rType=db(db.products.id==int(request.vars.item)).select(db.products.productType)[0].productType
    #Gets top 6 for that product
    query=db.products.productType.startswith(rType)
    similarProducts = db(query).select(orderby='products.productAvgRating DESC',limitby=(0,6))
    countSimi = db(query).count()
    
    #Gets total number of reviews for that product
    reviewNumber=db(db.product_reviews.productID == request.vars.item).count()
    #Gets top 10 latest reviews for that product
    rows = db(db.product_reviews.productID == request.vars.item).select(orderby='product_reviews.ID DESC', limitby=(0,10))
    return locals()

def viewReviews():
    bckButton = A(SPAN(_class='icon leftarrow icon-arrow-left glyphicon glyphicon-arrow-left'),' Back',_class='button btn btn-default',_href=URL("/viewProduct",vars={'item':request.vars.item}))

     #Makes sure the item variable is an integer
    try:
        float(request.vars['item']).is_integer()
    except:
        redirect(URL(vars={'item':1}))
    
    #Gets all reviews for that product
    reviewNumber=db(db.product_reviews.productID == request.vars.item).count()
    products = db(db.products.id == request.vars.item).select()
    rows = db(db.product_reviews.productID == request.vars.item).select(orderby='product_reviews.ID DESC')
    return locals()

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    #Adds captcha to pages
    auth.settings.captcha = Recaptcha2(request,'6LdnExsUAAAAABtu-GE-rZ56VtOZRx0xnuNSqjwu', '6LdnExsUAAAAAH7I5JDfZCg55h0PWrWYJkDuVFHA')
    auth.settings.login_captcha = None
    auth.settings.register_captcha = None
    auth.settings.retrieve_username_captcha = None
    auth.settings.retrieve_password_captcha = None
    
    #When a use signs up, they join normalUsers group. Seperate user groups are not created.
    auth.settings.everybody_group_id=1
    auth.settings.create_user_groups = None
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """	
    return service()

@auth.requires_membership('admins')
def manage():
    #View button redirects to viewProduct.html rather than default manage view. Grid created.
    links = [lambda row:A(SPAN(_class='icon magnifier icon-zoom-in glyphicon glyphicon-zoom-in'),' View',_class='button btn btn-default',_href=URL("viewProduct",vars={'item':row.id}))]
    grid = SQLFORM.grid(db.products,headers={'products.productName':'Name','products.productDescription':'Description','products.productImage':'Image 1','products.productImage2':'Image 2','products.productPrice':'Price (£)','products.productQuantity':'Quantity','products.productSize':'Size','products.productType':'Type','products.productAvgRating':'Average Rating'},deletable=auth.has_membership(group_id='2'),user_signature=False, links=links, editable=auth.has_membership(group_id='2'),details=False)
    
    #Changes the form depending on which part of the page the user is on
    if (request.args(0) =="edit"):
        form=SQLFORM(db.products,request.args(2),labels={'productName':'Name:','productDescription':'Description:','productImage':'Image 1:','productImage2':'Image 2:','productPrice':'Price (£):','productQuantity':'Quantity:','productSize':'Size:','productType':'Type:','productAvgRating':'Average Rating:'},showid=False,upload=URL('download')).process()
    if (request.args(0) =="new"):
        db.products.productAvgRating.default = 0
        db.products.productAvgRating.readable=False
        db.products.productAvgRating.writable=False
        form=SQLFORM(db.products,labels={'productName':'Name:','productDescription':'Description:','productImage':'Image 1:','productImage2':'Image 2:','productPrice':'Price (£):','productQuantity':'Quantity:','productSize':'Size:','productType':'Type:','productAvgRating':'Average Rating:'},showid=False,upload=URL('download')).process()
    return locals()
