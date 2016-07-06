import colander
import deform.widget

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.view import forbidden_view_config


from .models import DBSession, Page


from pyramid.security import (
    remember,
    forget,
    )

from .security import USERS

@view_defaults(renderer='home.pt')
class TutorialViews:
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid


class WikiPage(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget()
    )


class WikiViews(object):
    def __init__(self, request):
        self.request = request
        self.logged_in = request.authenticated_userid

    @property
    def wiki_form(self):
        schema = WikiPage()
        return deform.Form(schema, buttons=('submit',))
    
    @property
    def wiki_b3(self):
        schema = WikiPage()
        return deform.b3(schema, buttons=('remove seleted',))
 

    @property
    def reqts(self):
        return self.wiki_form.get_widget_resources()
   
   # @view_config(route_name='home', renderer='home.pt')
   # def home(self):
    #    pages = DBSession.query(Page).order_by(Page.title)
     #   return dict(title='Home View', pages=pages)
    
   # @view_config(route_name='edit', permission='edit')
   # def Edit(self):
       # return {'name': 'Hello View'}
       # return dict(title='Home View', pages=pages)

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
            message = 'Failed login/You may not have rights to edit'

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
        url = request.route_url('wiki_view')
        return HTTPFound(location=url,
                         headers=headers)

    
    @view_config(route_name='wiki_view', renderer='wiki_view.pt')
    def wiki_view(self):
        pages = DBSession.query(Page).order_by(Page.title)
        return dict(title='Wiki View', pages=pages)


    @view_config(route_name='wikipage_delete',permission='edit',renderer='wikipage_delete.pt')
    def wiki_delete(self):
       # import pdb; pdb.set_trace()
        if 'Delete' in self.request.params:
            for uid in self.request.params:
                if uid == 'Delete':
                    continue
                # remove = DBSession.query(Page).filter_by(uid).delete()
                page = DBSession.query(Page).filter_by(uid=uid).one()
                DBSession.delete(page)
                	
        pages = DBSession.query(Page).order_by(Page.title)
        return dict(title='Wiki Delete', pages=pages)



    @view_config(route_name='wikipage_add',permission='edit',
                 renderer='wikipage_addedit.pt')
    def wikipage_add(self):
        form = self.wiki_form.render()

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = self.wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid
                return dict(form=e.render())

            # Add a new page to the database
            new_title = appstruct['title']
            new_body = appstruct['body']
            DBSession.add(Page(title=new_title, body=new_body))

            # Get the new ID and redirect
            page = DBSession.query(Page).filter_by(title=new_title).one()
            new_uid = page.uid

            url = self.request.route_url('wikipage_view', uid=new_uid)
            return HTTPFound(url)

        return dict(form=form)


    @view_config(route_name='wikipage_view', renderer='wikipage_view.pt')
    def wikipage_view(self):
        uid = int(self.request.matchdict['uid'])
        page = DBSession.query(Page).filter_by(uid=uid).one()
        return dict(page=page)

    #@view_config(route_name='wikipage_delete',
    #               renderer='wikipage_delete.pt')
    #def wikipage_edit(self):
    #    uid = int(self.request.matchdict['uid'])
    #    page = DBSession.query(Page).filter_by(uid=uid).one()

    #    wiki_form = self.wiki_form

    #    if 'submit' in self.request.params:
    #        controls = self.request.POST.items()
    #        try:
    #            appstruct = wiki_form.validate(controls)
    #        except deform.ValidationFailure as e:
    #            return dict(page=page, form=e.render())

    #        # Change the content and redirect to the view
    #        page.title = appstruct['title']
    #        page.body = appstruct['body']
    #        url = self.request.route_url('wikipage_view', uid=uid)
    #        return HTTPFound(url)

    #    form = self.wiki_form.render(dict(
    #        uid=page.uid, title=page.title, body=page.body)
    #    )

    #    return dict(page=page, form=form)





    @view_config(route_name='wikipage_edit',permission='edit',
                 renderer='wikipage_addedit.pt',)
    def wikipage_edit(self):
        uid = int(self.request.matchdict['uid'])
        page = DBSession.query(Page).filter_by(uid=uid).one()

        wiki_form = self.wiki_form

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(page=page, form=e.render())

            # Change the content and redirect to the view
            page.title = appstruct['title']
            page.body = appstruct['body']
            url = self.request.route_url('wikipage_view', uid=uid)
            return HTTPFound(url)

        form = self.wiki_form.render(dict(
            uid=page.uid, title=page.title, body=page.body)
        )

        return dict(page=page, form=form)
