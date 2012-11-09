''' Demo of a Metro-style pivot view.

Inspired by Sami Makkonen in his blog post here:
http://qt.digia.com/Blogs/Qt-blog/Sami-Makkonen/Dates/2012/1/2012/
'''

import sys
import collections

from PySide import QtCore, QtGui
from PySide.QtCore import Qt

class Style:
    '''Style constants'''

    # margin for all ui components
    component_margin = 24
    
    body_text_size = 24
    header_text_size = 48
    
    # ui fonts and color
    header_font = QtGui.QFont("Segoe UI", header_text_size)
    body_font = QtGui.QFont("Segoe UI", body_text_size)
    ui_text_color = Qt.white
    background_style = "background-color: rgba(26,26,26)"
    # ui animation duration
    animation_time = 400

class PivotView(QtGui.QGraphicsView):
    def __init__(self, scene, tabs=None, parent=None):
        super(PivotView, self).__init__(scene, parent)
        
        self.tabs = tabs or {}

        self.header_items = []
        self.header_animations = []
        self.content_items = []
        self.content_animations = []
        
        self.current_item = 0
        self.mouse_x_position = 0
        
        #####
        # set blackish background
        self.setStyleSheet(Style.background_style)
    
        # create opacity animator
        self.opacity_animator = QtCore.QPropertyAnimation()
        self.opacity_animator.setDuration(Style.animation_time)
        self.opacity_animator.setPropertyName("opacity")
        self.opacity_animator.setEasingCurve(QtCore.QEasingCurve.Linear)
        self.opacity_animator.setStartValue(0.3)
        self.opacity_animator.setEndValue(1.0)

        # create animation groups
        self.group_animation_content = QtCore.QParallelAnimationGroup()
        self.group_animation_header = QtCore.QParallelAnimationGroup()
        
        # create the rest of the ui
        self._create_top_bar()
        self._create_metro_tab_bar()
        self._create_content_items()
        
    def _create_top_bar(self):
        bar = QtGui.QGraphicsTextItem()
        bar.setAcceptHoverEvents(False)
        bar.setFont(Style.body_font)
        bar.setPlainText("Python Metro Style Pivot")
        bar.setDefaultTextColor(Style.ui_text_color)
        bar.setPos(Style.component_margin, Style.component_margin)
        self.scene().addItem(bar)
        
    def _create_metro_tab_bar(self):
        x_pos = Style.component_margin
    
        # create pivot header items
        for i, text in enumerate(self.tabs.iterkeys()):
            text_item = QtGui.QGraphicsTextItem()
            text_item.setAcceptHoverEvents(False)
            text_item.setPlainText(text)
            text_item.setFont(Style.header_font)
            text_item.adjustSize()
            text_item.setDefaultTextColor(Style.ui_text_color)
    
            # place header below header text
            text_item.setPos(x_pos, (Style.component_margin* 2 + Style.body_text_size))
    
            # calculate position for the next item. ComponentMargin + item width + ComponentMargin
            x_pos = x_pos + text_item.textWidth() + Style.component_margin
    
            anim = QtCore.QPropertyAnimation(text_item, 'pos')
            anim.setDuration(Style.animation_time)
            anim.setPropertyName('pos')
            anim.setEasingCurve(QtCore.QEasingCurve.OutCirc)
            self.group_animation_header.addAnimation(anim)
            self.header_animations.append(anim)
    
            # remove highlight from all items except the current one
            if i > 0:
                text_item.setOpacity(0.3)
    
            self.header_items.append(text_item)
            self.scene().addItem(text_item)
            
            
    def _create_content_items(self):
        x_pos = Style.component_margin
        # scene width - margins
        text_width = self.scene().width() - 2 * Style.component_margin
    
        # create pivot items text
        for i, text in enumerate(self.tabs.itervalues()):
            tmp = QtGui.QGraphicsTextItem()
            tmp.setFont(Style.body_font)
            tmp.setAcceptHoverEvents(False)
            tmp.setPlainText(text)
            tmp.setTextWidth(text_width)
            tmp.setDefaultTextColor(Style.ui_text_color)
    
            # place content below header and pivot
            tmp.setPos(x_pos,(Style.component_margin * 4 +
                              Style.body_text_size + Style.header_text_size))
    
            # calculate the position for the next item
            x_pos = x_pos + text_width + Style.component_margin
    
            anim = QtCore.QPropertyAnimation(tmp, 'pos')
            anim.setDuration(Style.animation_time)
            anim.setPropertyName('pos')
            anim.setEasingCurve(QtCore.QEasingCurve.OutCirc)
    
            self.group_animation_content.addAnimation(anim)
            self.content_animations.append(anim)
            self.content_items.append(tmp)
            self.scene().addItem(tmp)
            
    def mousePressEvent(self, event):
        self.mouse_x_position = event.pos().x()
        
    def mouseMoveEvent(self, event):
        # move the header by the width of oen item
        calc_header_x_offset = lambda i: self.header_items[i].textWidth() + Style.component_margin
        
        # a negative value means the mouse moved left
        delta_x = event.pos().x() - self.mouse_x_position
    
        # don't start animations twice
        if (self.group_animation_content.state() != QtCore.QAbstractAnimation.Running and
            self.group_animation_header.state() != QtCore.QAbstractAnimation.Running):
            
            # sweep left 
            if delta_x < 0:
                # don't get over the edge
                if self.current_item < len(self.tabs) - 1:
                    # move the header by the width of the current item
                    header_x_offset = -calc_header_x_offset(self.current_item)
                    self.current_item += 1
                    self.start_content_animation(True)
                    self.start_header_animation(header_x_offset)
                
            # sweep right
            elif delta_x > 0:
                # don't get over the edge
                if self.current_item > 0:
                    self.current_item -= 1
                    # move the header by the width of the item being moved into place
                    header_x_offset = calc_header_x_offset(self.current_item)
                    self.start_content_animation(False)
                    self.start_header_animation(header_x_offset)
                    
        self.mouse_x_position = event.pos().x()
        
    def start_content_animation(self, sweep_left=True):
        # create animation items
        for i in xrange(len(self.tabs)):
            text = self.content_items[i]
            start = text.pos()
            end = text.pos()
            
            if sweep_left:
                end.setX(end.x() - text.textWidth() - Style.component_margin)
            else:
                end.setX(end.x() + text.textWidth() + Style.component_margin)
                
            self.content_animations[i].setStartValue(start)
            self.content_animations[i].setEndValue(end)
            
        self.group_animation_content.start()

    def start_header_animation(self, x_offset):
        for i in xrange(len(self.tabs)):
            text = self.header_items[i]
            start = text.pos()
            end = text.pos()
            end.setX(end.x() + x_offset)
                
            self.header_animations[i].setStartValue(start)
            self.header_animations[i].setEndValue(end)
            
            # reset opacity
            text.setOpacity(0.3)
            
        self.opacity_animator.setTargetObject(self.header_items[self.current_item])
        self.group_animation_header.start()
        self.opacity_animator.start()
        
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view_rect = QtCore.QRect(100, 100, 1366, 768)

    scene = QtGui.QGraphicsScene()
    scene.setSceneRect(0.0, 0.0, view_rect.width(), view_rect.height())
    
    tabs = collections.OrderedDict((('Summary',"Metro is an internal code name of a typography-based design language created by Microsoft, originally for use in Windows Phone 7. A key design principle of Metro is better focus on the content of applications, relying more on typography and less on graphics (\"content before chrome\"). Early uses of the Metro principles began as early as Microsoft Encarta 95 and MSN 2.0, and later evolved into Windows Media Center and Zune. Later the principles of Metro were included in Windows Phone, Microsoft's website, the Xbox 360 dashboard update, and Windows 8."),
            ('History',"Metro is based on the design principles of classic Swiss graphic design. Early glimpses of this style could be seen in Windows Media Center for Windows XP Media Center Edition, which favored text as the primary form of navigation. This interface carried over into later iterations of Media Center. In 2006, Zune refreshed its interface using these principles. Microsoft designers decided to redesign the interface and with more focus on clean typography and less on UI chrome. These principles and the new Zune UI were carried over to Windows Phone 7 (from which much was drawn for Windows 8). The Zune Desktop Client was also redesigned with an emphasis on typography and clean design that was different from the Zune's previous Portable Media Center based UI. Flat colored \"live tiles\" were introduced into the design language during the early Windows Phone's studies. Microsoft has begun integrating these elements of the design language into its other products, with direct influence being seen in newer versions of Windows Live Messenger, Live Mesh, and Windows 8."),
            ('Principles 1',"Microsoft's design team says that the design language is partly inspired by signs commonly found at public transport systems; for instance, those found on the King County Metro transit system, which serves the greater Seattle area where Microsoft is headquartered. The design language places emphasis on good typography and has large text that catches the eye. Microsoft says that the design language is designed to be \"sleek, quick, modern\" and a \"refresh\" from the icon-based interfaces of Windows, Android, and iOS. All instances use fonts based on the Segoe font family designed by Steve Matteson at Agfa Monotype and licensed to Microsoft. For the Zune, Microsoft created a custom version called Zegoe UI, and for Windows Phone, Microsoft created the \"Segoe WP\" font family. The fonts mostly differ only in minor details. More obvious differences between Segoe UI and Segoe WP are apparent in their respective numerical characters. The Segoe UI in Windows 8 had an obvious differences as being similar to Segoe WP. Notable characters had a typographic changes of the characters 1, 2, 4, 5, 7, 8, I, and Q."),
            ('Principles 2',"The design language was designed specifically to consolidate groups of common tasks to speed up usage. This is accomplished by excluding superfluous graphics and instead relying on the actual content to also function as the main UI. The resulting interfaces favour larger hubs over smaller buttons and often feature laterally scrolling canvases. Page titles are usually large and consequently also take advantage of lateral scrolling."),
            ('Principles 3',"Animation plays a large part, with transitions, and user interactions such as presses or swipes recommended to always be acknowledged by some form of natural animation or motion. This is intended to give the user the impression that the UI is \"alive\" and responsive, with \"an added sense of depth.\""),
            ('Principles 4',"Close to the official launch date of Windows 8 (October 26, 2012), more developers and Microsoft partners started working on creating new Metro applications, and many websites with resources related to this topic have been created, as well as the Microsoft's UX guidelines for Windows Store Apps."),
    ))
    
    view = PivotView(scene, tabs=tabs)
    view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    view.setGeometry(view_rect)
    view.setRenderHints(QtGui.QPainter.Antialiasing)
    view.show()
    
    app.exec_()