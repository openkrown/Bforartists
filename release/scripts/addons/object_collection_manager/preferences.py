# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright 2011, Ryan Inch

import bpy
from bpy.types import AddonPreferences
from bpy.props import (
    BoolProperty,
    FloatProperty,
    FloatVectorProperty,
    )

from . import qcd_init

def update_qcd_status(self, context):
    if self.enable_qcd:
        qcd_init.register_qcd()

        if self.enable_qcd_view_hotkeys:
            qcd_init.register_qcd_view_hotkeys()

    else:
        qcd_init.unregister_qcd()

def update_qcd_view_hotkeys_status(self, context):
    if self.enable_qcd_view_hotkeys:
        qcd_init.register_qcd_view_hotkeys()
    else:
        qcd_init.unregister_qcd_view_hotkeys()

def get_tool_text(self):
    if self.tool_text_override:
        return self["tool_text_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_tool.text
        self["tool_text_color"] = color.r, color.g, color.b
        return self["tool_text_color"]

def set_tool_text(self, values):
    self["tool_text_color"] = values[0], values[1], values[2]


def get_tool_text_sel(self):
    if self.tool_text_sel_override:
        return self["tool_text_sel_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_tool.text_sel
        self["tool_text_sel_color"] = color.r, color.g, color.b
        return self["tool_text_sel_color"]

def set_tool_text_sel(self, values):
    self["tool_text_sel_color"] = values[0], values[1], values[2]


def get_tool_inner(self):
    if self.tool_inner_override:
        return self["tool_inner_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_tool.inner
        self["tool_inner_color"] = color[0], color[1], color[2], color[3]
        return self["tool_inner_color"]

def set_tool_inner(self, values):
    self["tool_inner_color"] = values[0], values[1], values[2], values[3]


def get_tool_inner_sel(self):
    if self.tool_inner_sel_override:
        return self["tool_inner_sel_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_tool.inner_sel
        self["tool_inner_sel_color"] = color[0], color[1], color[2], color[3]
        return self["tool_inner_sel_color"]

def set_tool_inner_sel(self, values):
    self["tool_inner_sel_color"] = values[0], values[1], values[2], values[3]


def get_tool_outline(self):
    if self.tool_outline_override:
        return self["tool_outline_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_tool.outline
        self["tool_outline_color"] = color.r, color.g, color.b
        return self["tool_outline_color"]

def set_tool_outline(self, values):
    self["tool_outline_color"] = values[0], values[1], values[2]


def get_menu_back_text(self):
    if self.menu_back_text_override:
        return self["menu_back_text_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_menu_back.text
        self["menu_back_text_color"] = color.r, color.g, color.b
        return self["menu_back_text_color"]

def set_menu_back_text(self, values):
    self["menu_back_text_color"] = values[0], values[1], values[2]


def get_menu_back_inner(self):
    if self.menu_back_inner_override:
        return self["menu_back_inner_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_menu_back.inner
        self["menu_back_inner_color"] = color[0], color[1], color[2], color[3]
        return self["menu_back_inner_color"]

def set_menu_back_inner(self, values):
    self["menu_back_inner_color"] = values[0], values[1], values[2], values[3]


def get_menu_back_outline(self):
    if self.menu_back_outline_override:
        return self["menu_back_outline_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_menu_back.outline
        self["menu_back_outline_color"] = color.r, color.g, color.b
        return self["menu_back_outline_color"]

def set_menu_back_outline(self, values):
    self["menu_back_outline_color"] = values[0], values[1], values[2]


def get_tooltip_text(self):
    if self.tooltip_text_override:
        return self["tooltip_text_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_tooltip.text
        self["tooltip_text_color"] = color.r, color.g, color.b
        return self["tooltip_text_color"]

def set_tooltip_text(self, values):
    self["tooltip_text_color"] = values[0], values[1], values[2]


def get_tooltip_inner(self):
    if self.tooltip_inner_override:
        return self["tooltip_inner_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_tooltip.inner
        self["tooltip_inner_color"] = color[0], color[1], color[2], color[3]
        return self["tooltip_inner_color"]

def set_tooltip_inner(self, values):
    self["tooltip_inner_color"] = values[0], values[1], values[2], values[3]


def get_tooltip_outline(self):
    if self.tooltip_outline_override:
        return self["tooltip_outline_color"]
    else:
        color = bpy.context.preferences.themes[0].user_interface.wcol_tooltip.outline
        self["tooltip_outline_color"] = color.r, color.g, color.b
        return self["tooltip_outline_color"]

def set_tooltip_outline(self, values):
    self["tooltip_outline_color"] = values[0], values[1], values[2]


class CMPreferences(AddonPreferences):
    bl_idname = __package__

    # ENABLE QCD BOOLS
    enable_qcd: BoolProperty(
        name="QCD",
        description="Enable/Disable QCD System.\nThe Quick Content Display system allows you to specify collections as QCD \"slots\" up to a maximum of 20. You can then interact with them through numerical hotkeys, a popup move widget, and a 3D View header widget",
        default=True,
        update=update_qcd_status,
        )

    enable_qcd_view_hotkeys: BoolProperty(
        name="QCD Hotkeys",
        description="Enable/Disable the numerical hotkeys to view QCD slots",
        default=True,
        update=update_qcd_view_hotkeys_status,
        )


    # OVERRIDE BOOLS
    tool_text_override: BoolProperty(
        name="Text",
        description="Override Theme Text Color",
        default=False,
        )

    tool_text_sel_override: BoolProperty(
        name="Selection",
        description="Override Theme Text Selection Color",
        default=False,
        )

    tool_inner_override: BoolProperty(
        name="Inner",
        description="Override Theme Inner Color",
        default=False,
        )

    tool_inner_sel_override: BoolProperty(
        name="Selection",
        description="Override Theme Inner Selection Color",
        default=False,
        )

    tool_outline_override: BoolProperty(
        name="Outline",
        description="Override Theme Outline Color",
        default=False,
        )

    menu_back_text_override: BoolProperty(
        name="Text",
        description="Override Theme Text Color",
        default=False,
        )

    menu_back_inner_override: BoolProperty(
        name="Inner",
        description="Override Theme Inner Color",
        default=False,
        )

    menu_back_outline_override: BoolProperty(
        name="Outline",
        description="Override Theme Outline Color",
        default=False,
        )

    tooltip_text_override: BoolProperty(
        name="Text",
        description="Override Theme Text Color",
        default=False,
        )

    tooltip_inner_override: BoolProperty(
        name="Inner",
        description="Override Theme Inner Color",
        default=False,
        )

    tooltip_outline_override: BoolProperty(
        name="Outline",
        description="Override Theme Outline Color",
        default=False,
        )


    # OVERRIDE COLORS
    qcd_ogl_widget_tool_text: FloatVectorProperty(
        name="",
        description="QCD Move Widget Tool Text Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_tool.text,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        get=get_tool_text,
        set=set_tool_text,
        )

    qcd_ogl_widget_tool_text_sel: FloatVectorProperty(
        name="",
        description="QCD Move Widget Tool Text Selection Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_tool.text_sel,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        get=get_tool_text_sel,
        set=set_tool_text_sel,
        )

    qcd_ogl_widget_tool_inner: FloatVectorProperty(
        name="",
        description="QCD Move Widget Tool Inner Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_tool.inner,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        size=4,
        get=get_tool_inner,
        set=set_tool_inner,
        )

    qcd_ogl_widget_tool_inner_sel: FloatVectorProperty(
        name="",
        description="QCD Move Widget Tool Inner Selection Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_tool.inner_sel,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        size=4,
        get=get_tool_inner_sel,
        set=set_tool_inner_sel,
        )

    qcd_ogl_widget_tool_outline: FloatVectorProperty(
        name="",
        description="QCD Move Widget Tool Outline Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_tool.outline,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        get=get_tool_outline,
        set=set_tool_outline,
        )

    qcd_ogl_widget_menu_back_text: FloatVectorProperty(
        name="",
        description="QCD Move Widget Menu Back Text Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_menu_back.text,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        get=get_menu_back_text,
        set=set_menu_back_text,
        )

    qcd_ogl_widget_menu_back_inner: FloatVectorProperty(
        name="",
        description="QCD Move Widget Menu Back Inner Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_menu_back.inner,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        size=4,
        get=get_menu_back_inner,
        set=set_menu_back_inner,
        )

    qcd_ogl_widget_menu_back_outline: FloatVectorProperty(
        name="",
        description="QCD Move Widget Menu Back Outline Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_menu_back.outline,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        get=get_menu_back_outline,
        set=set_menu_back_outline,
        )

    qcd_ogl_widget_tooltip_text: FloatVectorProperty(
        name="",
        description="QCD Move Widget Tooltip Text Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_tooltip.text,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        get=get_tooltip_text,
        set=set_tooltip_text,
        )

    qcd_ogl_widget_tooltip_inner: FloatVectorProperty(
        name="",
        description="QCD Move Widget Tooltip Inner Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_tooltip.inner,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        size=4,
        get=get_tooltip_inner,
        set=set_tooltip_inner,
        )

    qcd_ogl_widget_tooltip_outline: FloatVectorProperty(
        name="",
        description="QCD Move Widget Tooltip Outline Color",
        default=bpy.context.preferences.themes[0].user_interface.wcol_tooltip.outline,
        subtype='COLOR_GAMMA',
        min=0.0,
        max=1.0,
        get=get_tooltip_outline,
        set=set_tooltip_outline,
        )

    # NON ACTIVE ICON ALPHA
    qcd_ogl_selected_icon_alpha: FloatProperty(
        name="Selected Icon Alpha",
        description="Set the 'Selected' icon's alpha value",
        default=0.9,
        min=0.0,
        max=1.0,
        )

    qcd_ogl_objects_icon_alpha: FloatProperty(
        name="Objects Icon Alpha",
        description="Set the 'Objects' icon's alpha value",
        default=0.5,
        min=0.0,
        max=1.0,
        )

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        box.row().prop(self, "enable_qcd")

        if not self.enable_qcd:
            return

        box.row().prop(self, "enable_qcd_view_hotkeys")

        box.row().label(text="QCD Move Widget")

        tool_box = box.box()
        tool_box.row().label(text="Tool Theme Overrides:")
        tool_box.use_property_split = True

        flow = tool_box.grid_flow(row_major=False, columns=2, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.alignment = 'LEFT'

        row = col.row(align=True)
        row.alignment = 'RIGHT'
        row.prop(self, "tool_text_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.tool_text_override
        row.prop(self, "qcd_ogl_widget_tool_text")

        row = col.row(align=True)
        row.alignment = 'RIGHT'
        row.prop(self, "tool_text_sel_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.tool_text_sel_override
        row.prop(self, "qcd_ogl_widget_tool_text_sel")

        col = flow.column()
        col.alignment = 'RIGHT'

        row = col.row()
        row.alignment = 'RIGHT'
        row.prop(self, "tool_inner_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.tool_inner_override
        row.prop(self, "qcd_ogl_widget_tool_inner")

        row = col.row()
        row.alignment = 'RIGHT'
        row.prop(self, "tool_inner_sel_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.tool_inner_sel_override
        row.prop(self, "qcd_ogl_widget_tool_inner_sel")

        row = col.row()
        row.alignment = 'RIGHT'
        row.prop(self, "tool_outline_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.tool_outline_override
        row.prop(self, "qcd_ogl_widget_tool_outline")

        tool_box.use_property_split = False
        tool_box.row().label(text="Icon Alpha:")
        icon_fade_row = tool_box.row()
        icon_fade_row.alignment = 'EXPAND'
        icon_fade_row.prop(self, "qcd_ogl_selected_icon_alpha", text="Selected")
        icon_fade_row.prop(self, "qcd_ogl_objects_icon_alpha", text="Objects")


        menu_back_box = box.box()
        menu_back_box.use_property_split = True
        menu_back_box.row().label(text="Menu Back Theme Overrides:")

        flow = menu_back_box.grid_flow(row_major=False, columns=2, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.alignment = 'LEFT'

        row = col.row(align=True)
        row.alignment = 'RIGHT'
        row.prop(self, "menu_back_text_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.menu_back_text_override
        row.prop(self, "qcd_ogl_widget_menu_back_text")

        col = flow.column()
        col.alignment = 'RIGHT'

        row = col.row()
        row.alignment = 'RIGHT'
        row.prop(self, "menu_back_inner_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.menu_back_inner_override
        row.prop(self, "qcd_ogl_widget_menu_back_inner")

        row = col.row()
        row.alignment = 'RIGHT'
        row.prop(self, "menu_back_outline_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.menu_back_outline_override
        row.prop(self, "qcd_ogl_widget_menu_back_outline")


        tooltip_box = box.box()
        tooltip_box.use_property_split = True
        tooltip_box.row().label(text="Tooltip Theme Overrides:")

        flow = tooltip_box.grid_flow(row_major=False, columns=2, even_columns=True, even_rows=False, align=False)

        col = flow.column()
        col.alignment = 'LEFT'

        row = col.row(align=True)
        row.alignment = 'RIGHT'
        row.prop(self, "tooltip_text_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.tooltip_text_override
        row.prop(self, "qcd_ogl_widget_tooltip_text")

        col = flow.column()
        col.alignment = 'RIGHT'

        row = col.row()
        row.alignment = 'RIGHT'
        row.prop(self, "tooltip_inner_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.tooltip_inner_override
        row.prop(self, "qcd_ogl_widget_tooltip_inner")

        row = col.row()
        row.alignment = 'RIGHT'
        row.prop(self, "tooltip_outline_override")
        row = row.row(align=True)
        row.alignment = 'RIGHT'
        row.enabled = self.tooltip_outline_override
        row.prop(self, "qcd_ogl_widget_tooltip_outline")
