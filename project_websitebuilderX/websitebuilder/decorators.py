from django.shortcuts import redirect

def user_not_authenticated(function=None, redirect_url='/'):
    """
    Decorator for views that checks that the user is NOT logged in, redirecting
    to the homepage if necessary by default.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
                
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    if function:
        return decorator(function)

    return decorator






def notLoggedUsers(view_func):
    def wrapper_func(request , *args,**kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return view_func(request , *args,**kwargs)
    return wrapper_func




def allowedUsers(allowedGroups=[]):
    def decorator(view_func):
        def wrapper_func(request , *args,**kwargs): 
            group = None
            if request.user.groups.exists():
               group =  request.user.groups.all()[0].name
            if group in allowedGroups:
               return view_func(request , *args,**kwargs)
            else:
                return redirect('/')
            
        return wrapper_func
    return decorator


def forAdmins(view_func): 
        def wrapper_func(request , *args,**kwargs): 
            group = None
            if request.user.groups.exists():
               group =  request.user.groups.all()[0].name
            if group == 'admin':
               return view_func(request , *args,**kwargs)
            if group == 'customer':
                return redirect('dashboard')
            
        return wrapper_func 
    
    
    


def anonymous_required(view_func):
    """
    Decorator to redirect logged-in users away from the view.
    """
    def wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.filter(name='SuperAdmin').exists():
                # Redirect users in the 'SuperAdmin' group to '/home'
                return redirect('/homeSuperAdmin')
            if request.user.groups.filter(name='Cliente').exists():
                # Redirect users in the 'Cliente' group to '/home'
                return redirect('/home')
            if request.user.groups.filter(name='SupportTechnique').exists():
                # Redirect users in the 'SupportTechnique' group to '/home'
                return redirect('/homeSupportTechnique')
            if request.user.groups.filter(name='GestionnaireComptes').exists():
                # Redirect users in the 'GestionnaireComptes' group to '/home'
                return redirect('/homeGestionnairesComptes')
        return view_func(request, *args, **kwargs)
    return wrapped_view