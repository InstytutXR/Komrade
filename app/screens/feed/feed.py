from kivymd.uix.label import MDLabel
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import AsyncImage, Image
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard, MDSeparator
from kivy.uix.scrollview import ScrollView
from screens.base import ProtectedScreen,BaseScreen
from kivy.properties import ListProperty
import os,time
from datetime import datetime
from kivy.app import App
from threading import Thread
import asyncio
from misc import *
from kivy.core.window import Window



### POST CODE
class PostTitle(MDLabel): pass
class PostGridLayout(GridLayout): pass
class PostImage(AsyncImage): pass
# class PostImage(CoreImage)
class PostImageBytes(Image): pass

class PostContent(MDLabel): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.bind(texture_size=self.setter('size'))
        self.font_name='assets/overpass-mono-regular.otf'
    #pass

class PostAuthorLayout(MDBoxLayout): pass

class PostImageLayout(MDBoxLayout): pass


class PostAuthorLabel(MDLabel): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.bind(texture_size=self.setter('size'))
        self.font_name='assets/overpass-mono-regular.otf'
        #self.to_changeable=False

    def on_touch_down(self, touch):
        '''Receive a touch down event.
        :Parameters:
            `touch`: :class:`~kivy.input.motionevent.MotionEvent` class
                Touch received. The touch is in parent coordinates. See
                :mod:`~kivy.uix.relativelayout` for a discussion on
                coordinate systems.
        :Returns: bool
            If True, the dispatching of the touch event will stop.
            If False, the event will continue to be dispatched to the rest
            of the widget tree.
        '''
        #if not self.to_changeable: return
        # try:
        #     self.parent.parent.author_dialog.open()
        #     #for item in self.parent.parent.author_dialog.items:
        #     #    raise Exception([item.disabled, item.text])
        # except AttributeError:
        #     pass
        try:
            self.parent.parent.parent.open_author_option()
        except AttributeError:
            pass

        #raise Exception(self.text)
        # self.text = '!!!'
        
        #self.parent.parent.recipient
        #return
        #raise Exception(self.parent.parent.recipient)


        if self.disabled and self.collide_point(*touch.pos):
            return True
        for child in self.children[:]:
            if child.dispatch('on_touch_down', touch):
                return True

    pass

class PostTimestampLabel(MDLabel): 
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.bind(width=lambda s, w: s.setter('text_size')(s, (w, None)))
        self.bind(texture_size=self.setter('size'))
        self.font_name='assets/overpass-mono-regular.otf'

class PostAuthorAvatar(AsyncImage): pass

class PostLayout(MDBoxLayout): pass

class PostScrollView(ScrollView): pass

class PostCard(MDCard):
    @property
    def app(self): return App.get_running_app()
    def log(self,*x): self.app.log(*x)

    def __init__(self, data):
        super().__init__()
        # self.log('PostCard() got data: '+str(data))
        self.author = data.get('author','[Anonymous]')
        self.recipient = data.get('to_name','')
        if not self.recipient:
            self.recipient=self.app.channel

        self.img_id = data.get('file_id','')
        self.img_ext = data.get('file_ext','')
        self.img_src=self.img_id[:3]+'/'+self.img_id[3:]+'.'+self.img_ext if self.img_id else ''
        self.cache_img_src = os.path.join('cache',self.img_src) if self.img_src else ''
        self.img_loaded = os.path.exists(self.cache_img_src)
        self.content = data.get('content','')
        self.timestamp = data.get('timestamp',None)
        self.bind(minimum_height=self.setter('height'))
        
        
        # minwidth = 400
        # maxwidth = 800
        # abouts = int(Window.size[0]/1.5)
        # if abouts < minwidth: self.width=f'{minwidth}sp'
        # if abouts > maxwidth: self.width=f'{maxwidth}sp'
        # self.width=f'{abouts}sp'
    

        # self.log('PostCard.img_id =',self.img_id)
        # self.log('PostCard.img_ext =',self.img_ext)
        # self.log('PostCard.img_src =',self.img_src)
        # self.log('PostCard.cache_img_src =',self.cache_img_src)

        # pieces
        self.author_section_layout = author_section_layout = PostAuthorLayout()
        self.author_label = author_label = PostAuthorLabel(text='@'+self.author)
        self.author_label.font_name='assets/overpass-mono-semibold.otf'
        if self.recipient:
            recip=self.recipient
            recip='@'+recip if recip and recip[0].isalpha() else recip
            self.author_label.text+='\n[size=14sp]to '+recip+'[/size]'
            self.author_label.markup=True
        self.author_label.font_size = '18sp'
        self.author_avatar = author_avatar = PostAuthorAvatar(source=f'assets/avatars/{self.author}.png') #self.img_src)
        self.author_section_layout.add_widget(author_avatar)
        self.author_section_layout.add_widget(author_label)
        # self.author_section_layout.add_widget(MDSeparator(height='1sp',size_hint=(None,None)))

        # self.recipient_label = author_label = PostAuthorLabel(text='--> @'+self.recipient)
        # self.recipient_label.font_size = '14sp'
        # self.author_label.add_widget(self.recipient_label)
        

        # timestamp
        timestr=''
        #log(self.timestamp)
        if self.timestamp:
            dt_object = datetime.fromtimestamp(self.timestamp)
            timestr = dt_object.strftime("%-d %b %Y %H:%M") 
            #log('timestr: '+timestr)
            self.timestamp_label=PostTimestampLabel(text=timestr)
            self.timestamp_label.font_size='14sp'
            author_section_layout.add_widget(self.timestamp_label)
        # author_section_layout.add_widget(author_avatar)
        # self.add_widget(author_section_layout)

        if self.cache_img_src:
            image_layout = PostImageLayout()
            self.image = image = PostImage(source=self.cache_img_src)
            image.height = '300sp'
            image_layout.add_widget(image)
            image_layout.height='300sp'
            # self.log(image.image_ratio)

        self.post_content = PostContent(text=self.content)
        
        # post_layout = PostGridLayout()
        #content = PostContent()

        # add to screen
        # self.add_widget(title)
        # post_layout.add_widget(author_section_layout)
        # post_layout.add_widget(image_layout)
        # post_layout.add_widget(content)

        
        self.scroller = scroller = PostScrollView()
        self.add_widget(author_section_layout)
        # self.add_widget(MDLabel(text='hello'))
        #log('img_src ' + str(bool(self.img_src)))
        if self.img_src: self.add_widget(image_layout)

        def estimate_height(minlen=100,maxlen=300):
            num_chars = len(self.content)
            # num_lines = num_chars
            height = num_chars*1.1
            if height>maxlen: height=maxlen
            if height<minlen: height=minlen
            return height

        scroller.size = ('300sp','%ssp' % estimate_height())
        

        # scroller.bind(size=('300sp',scroller.setter('height'))
        scroller.add_widget(self.post_content)
        self.add_widget(scroller)
        # self.add_widget(post_layout)

        # self.log('?????',self.cache_img_src, os.path.exists(self.cache_img_src), os.stat(self.cache_img_src).st_size)
        if self.cache_img_src and (not os.path.exists(self.cache_img_src) or not os.stat(self.cache_img_src).st_size):
            async def do_download_later():
                self.log('downloading...')
                await self.app.download(self.img_id, self.cache_img_src)
                self.image.reload()
                return True

            #self.open_dialog('posting')
            #Thread(target=do_download).start()
            asyncio.create_task(do_download_later())


    @property
    def app(self):
        return App.get_running_app()

    def load_image(self):
        if not self.img_src: return
        if self.img_loaded: return
        
        # otherwise load image...
        self.app.get_image(self.img_src)
        self.log('done getting image!')
        self.image.reload()
        self.img_loaded=True

#####


class FeedScreen(BaseScreen):
    posts = ListProperty()

    def on_pre_enter(self):
        super().on_pre_enter()
        
        async def go():
            # self.log('ids:' +str(self.ids.post_carousel.ids))
            for post in self.posts:
                self.ids.post_carousel.remove_widget(post)
            
            i=0
            lim=25
            posts=await self.app.get_posts(self.app.uri)
            for i,post in enumerate(reversed(posts)):
            # for i,post in enumerate(posts)):
                #if ln.startswith('@') or ln.startswith('RT '): continue
                #i+=1
                if i>lim: break
                
                #post = Post(title=f'Marx Zuckerberg', content=ln.strip())
                #self.log('???')
                post_obj = PostCard(post)
                self.posts.append(post_obj)
                self.ids.post_carousel.add_widget(post_obj)
        asyncio.create_task(go())

