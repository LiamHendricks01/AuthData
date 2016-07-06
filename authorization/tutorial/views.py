import colander
import deform.widget

from pyramid.httpexceptions import HTTPFound
from .models import DBSession, Page

from pyramid.security import (
    remember,
    forget,
    )

from pyramid.view import (
    view_config,
    view_defaults,
    forbidden_view_config
    )

from .security import USERS


@view_defaults(renderer='home.pt')
class TutorialViews:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid
    


    @view_config(route_name='home',renderer='home.pt')
    def home(self):
        pages = DBSession.query(Page).order_by(Page.title)
        return {'name':'Wiki'}
        
    
    @view_config(route_name='wiki_view', renderer='wiki_view.pt')
    def wiki_view(self):
        pages = DBSession.query(Page).order_by(Page.title)
        return dict(title='Wiki View', pages=pages)



    @view_config(route_name='wikipage_view', renderer='wikipage_view.pt')
    def wikipage_view(self):
        uid = int(self.request.matchdict['uid'])
        page = DBSession.query(Page).filter_by(uid=uid).one() 
        return dict(page=page)


    @view_config(route_name='hello', permission='edit')
    def hello(self):
        return {'name': 'Hello View'}

    @view_config(route_name='login', renderer='login.pt')
    @forbidden_view_config(renderer='login.pt')
    def login(self):
        request = self.request
        login_url = request.route_url('login')
        referrer = request.url
        if referrer == login_url:
            referrer = '/'  # never use login form itself as came_from
        came_from = request.params.get('came_from', referrer)
        message = ''
        login = ''
        password = ''
        if 'form.submitted' in request.params:
            login = request.params['login']
            password = request.params['password']
            if USERS.get(login) == password:
                headers = remember(request, login)
                return HTTPFound(location=came_from,
                                 headers=headers)
            message = 'Failed login'

        return dict(
            name='Login',
            message=message,
            url=request.application_url + '/login',
            came_from=came_from,
            login=login,
            password=password,
        )

    @view_config(route_name='logout')
    def logout(self):
        request = self.request
        headers = forget(request)
        url = request.route_url('home')
        return HTTPFound(location=url,
                         headers=headers)

