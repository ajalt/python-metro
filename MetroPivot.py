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
        
        self.current_index = 0
        self.mouse_x_position = 0
        self.prev_x_position = 0
        
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
        self.content_animation_group = QtCore.QParallelAnimationGroup()
        self.header_animation_group = QtCore.QParallelAnimationGroup()
        
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
            self.header_animation_group.addAnimation(anim)
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
    
            self.content_animation_group.addAnimation(anim)
            self.content_animations.append(anim)
            self.content_items.append(tmp)
            self.scene().addItem(tmp)
            
    def mousePressEvent(self, event):
        self.prev_x_position = self.mouse_x_position = event.pos().x()
        
    def mouseMoveEvent(self, event):
        # don't do anything if there's an animation going
        if self.content_animation_group.state() != QtCore.QAbstractAnimation.Running:
            delta_x = event.x() - self.prev_x_position
            self.prev_x_position = event.x()
            
            # Keep the content under the mouse until it's released.
            for item in self.content_items:
                item.moveBy(delta_x, 0)
        
    def mouseReleaseEvent(self, event):
        # don't start animations twice
        if (self.content_animation_group.state() != QtCore.QAbstractAnimation.Running and
            self.header_animation_group.state() != QtCore.QAbstractAnimation.Running):
            
            # a negative value means the mouse moved left
            delta_x = event.x() - self.mouse_x_position
            sign_x = -1 if delta_x < 0 else 1
            
            # if we aren't trying to scroll off the end, move everything
            if ((delta_x < 0 and self.current_index < len(self.tabs) - 1) or
                (delta_x > 0 and self.current_index > 0)):
            
                # move the content by the width of one item
                content_x_offset = self.content_items[self.current_index].textWidth() + Style.component_margin - abs(delta_x)
                # move the headers by the width of the current item if we're moving them left, or the previous item if we're moving them right
                header_x_offset = self.header_items[self.current_index - (1 if delta_x > 0 else 0)].textWidth() + Style.component_margin
                
                # if the mouse moved left, move the everything right and vice versa
                self.current_index -= sign_x
                    
                self.start_content_animation(sign_x * content_x_offset)
                self.start_header_animation(sign_x * header_x_offset)
            else:
                # if we're off the end, move the content back into place
                self.start_content_animation(-delta_x)
                    
        
    def start_content_animation(self, x_offset):
        # create animation items
        for i, item in enumerate(self.content_items):
            start = item.pos()
            end = item.pos()
            end.setX(end.x() + x_offset)
                
            self.content_animations[i].setStartValue(start)
            self.content_animations[i].setEndValue(end)
            
        self.content_animation_group.start()

    def start_header_animation(self, x_offset):
        for i, item in enumerate(self.header_items):
            start = item.pos()
            end = item.pos()
            end.setX(end.x() + x_offset)
                
            self.header_animations[i].setStartValue(start)
            self.header_animations[i].setEndValue(end)
            
            # reset opacity
            item.setOpacity(0.3)
            
        self.opacity_animator.setTargetObject(self.header_items[self.current_index])
        self.header_animation_group.start()
        self.opacity_animator.start()
        
        

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    view_rect = QtCore.QRect(100, 100, 1366, 768)

    scene = QtGui.QGraphicsScene()
    scene.setSceneRect(0.0, 0.0, view_rect.width(), view_rect.height())
    
    tabs = collections.OrderedDict((('Summary',"Metro is an internal code name of a typography-based design language created by Microsoft, originally for use in Windows Phone 7. A key design principle of Metro is better focus on the content of applications, relying more on typography and less on graphics (\"content before chrome\"). Early uses of the Metro principles began as early as Microsoft Encarta 95 and MSN 2.0, and later evolved into Windows Media Center and Zune. Later the principles of Metro were included in Windows Phone, Microsoft's website, the Xbox 360 dashboard update, and Windows 8."),
            ('History',"Metro is based on the design principles of classic Swiss graphic design. Early glimpses of this style could be seen in Windows Media Center for Windows XP Media Center Edition, which favored text as the primary form of navigation. This interface carried over into later iterations of Media Center. In 2006, Zune refreshed its interface using these principles. Microsoft designers decided to redesign the interface and with more focus on clean typography and less on UI chrome. These principles and the new Zune UI were carried over to Windows Phone 7 (from which much was drawn for Windows 8). The Zune Desktop Client was also redesigned with an emphasis on typography and clean design that was different from the Zune's previous Portable Media Center based UI. Flat colored \"live tiles\" were introduced into the design language during the early Windows Phone's studies. Microsoft has begun integrating these elements of the design language into its other products, with direct influence being seen in newer versions of Windows Live Messenger, Live Mesh, and Windows 8."),
            ('Principles 1',"Microsoft's design team says that the design language is partly inspired by signs commonly found at public transport systems; for instance, those found on the King County Metro transit system, which serves the greater Seattle area where Microsoft is headquartered. The design language places emphasis on good typography and has large text that catches the eye. Microsoft says that the design language is designed to be \"sleek, quick, modern\" and a \"refresh\" from the icon-based interfaces of Windows, Android, and iOS. All instances use fonts based on the Segoe font family designed by Steve Matteson at Agfa Monotype and licensed to Microsoft. For the Zune, Microsoft created a custom version called Zegoe UI, and for Windows Phone, Microsoft created the \"Segoe WP\" font family. The fonts mostly differ only in minor details. More obvious differences between Segoe UI and Segoe WP are apparent in their respective numerical characters. The Segoe UI in Windows 8 had an obvious differences as being similar to Segoe WP. Notable characters had a typographic changes of the characters 1, 2, 4, 5, 7, 8, I, and Q."),
            ('Principles 2',"The design language was designed specifically to consolidate groups of common tasks to speed up usage. This is accomplished by excluding superfluous graphics and instead relying on the actual content to also function as the main UI. The resulting interfaces favor larger hubs over smaller buttons and often feature laterally scrolling canvases. Page titles are usually large and consequently also take advantage of lateral scrolling."),
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