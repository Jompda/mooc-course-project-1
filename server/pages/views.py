from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.db import transaction, connection
from .models import Account

# A03:2021-Injection: Vulnerable to SQL injection which propagates to functions using this function.
# Fix by using django orm.
@transaction.atomic
def transfer(sender, receiver, amount):
	if sender == receiver:
		return

	cursor = connection.cursor()
	cursor.execute("SELECT balance FROM pages_account WHERE id = %s" % sender)
	acc1_balance = cursor.fetchone()[0]
	cursor.execute("SELECT balance FROM pages_account WHERE id = %s" % receiver)
	acc2_balance = cursor.fetchone()[0]

	if amount <= 0:
		return
	if acc1_balance < amount:
		return

	cursor.execute("UPDATE pages_account SET balance = '%s' WHERE id = %s" % (acc1_balance - amount, sender))
	cursor.execute("UPDATE pages_account SET balance = '%s' WHERE id = %s" % (acc2_balance + amount, receiver))
# END OF A03:2021-Injection


# A01:2021-Broken access control: Allows users to performs tasks not in their scope.
# Fix by using session
@login_required
def transferView(request):
	#request.session['to'] = request.GET.get('to')
	#request.session['amount'] = int(request.GET.get('amount'))
	return render(request, 'pages/confirm.html', {
		'sender': request.user.account.id,
		'receiver': User.objects.get(username=request.GET.get('to')).account.id,
		'amount': request.GET.get('amount')
	})

@login_required
def confirmView(request):
	# User-supplied ids
	# fix by getting ids from request.user and request.session['to']
	sender_id = request.GET.get('sender')
	receiver_id = request.GET.get('receiver')
	amount = int(request.GET.get('amount'))
	transfer(sender_id, receiver_id, amount)
	Account.objects.get(id=sender_id).refresh_from_db()
	Account.objects.get(id=receiver_id).refresh_from_db()
	return redirect('/')
# END OF A01:2021-Broken access control


# A07:2021-Identification and Authentication Failures: Allows brute-force attacks
# Fix by keeping track of login attempts by ip-address.
"""
Decorator @login_required from django.contrib.auth.decorators
def login_required(
    function=None, redirect_field_name=REDIRECT_FIELD_NAME, login_url=None
):
    #Decorator for views that checks that the user is logged in, redirecting
    #to the log-in page if necessary.

    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated,
        login_url=login_url,
        redirect_field_name=redirect_field_name,
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
"""
@login_required
# END OF A07:2021-Identification and Authentication Failures
def homePageView(request):
	accounts = Account.objects.exclude(user_id=request.user.id)
	return render(request, 'pages/index.html', {'accounts': accounts})



# To illustrate CSRF
def csrfView(request):
	return render(request, 'static/csrf.html')
