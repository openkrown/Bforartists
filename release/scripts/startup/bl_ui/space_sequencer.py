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

# <pep8 compliant>
import bpy
from bpy.types import (
    Header,
    Menu,
    Panel,
)
from bpy.app.translations import (
    contexts as i18n_contexts,
    pgettext_iface as iface_,
)
from bl_ui.properties_grease_pencil_common import (
    AnnotationDataPanel,
    GreasePencilToolsPanel,
)
from rna_prop_ui import PropertyPanel


def act_strip(context):
    try:
        return context.scene.sequence_editor.active_strip
    except AttributeError:
        return None


def selected_sequences_len(context):
    selected_sequences = getattr(context, "selected_sequences", None)
    if selected_sequences is None:
        return 0
    return len(selected_sequences)


def draw_color_balance(layout, color_balance):

    layout.use_property_split = False

    flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
    col = flow.column()

    box = col.box()
    split = box.split(factor=0.35)
    col = split.column(align=True)
    col.label(text="Lift:")
    col.separator()
    col.separator()
    col.prop(color_balance, "lift", text="")
    col.prop(color_balance, "invert_lift", text="Invert", icon='ARROW_LEFTRIGHT')
    split.template_color_picker(color_balance, "lift", value_slider=True, cubic=True)

    col = flow.column()

    box = col.box()
    split = box.split(factor=0.35)
    col = split.column(align=True)
    col.label(text="Gamma:")
    col.separator()
    col.separator()
    col.prop(color_balance, "gamma", text="")
    col.prop(color_balance, "invert_gamma", text="Invert", icon='ARROW_LEFTRIGHT')
    split.template_color_picker(color_balance, "gamma", value_slider=True, lock_luminosity=True, cubic=True)

    col = flow.column()

    box = col.box()
    split = box.split(factor=0.35)
    col = split.column(align=True)
    col.label(text="Gain:")
    col.separator()
    col.separator()
    col.prop(color_balance, "gain", text="")
    col.prop(color_balance, "invert_gain", text="Invert", icon='ARROW_LEFTRIGHT')
    split.template_color_picker(color_balance, "gain", value_slider=True, lock_luminosity=True, cubic=True)


class SEQUENCER_HT_header(Header):
    bl_space_type = 'SEQUENCE_EDITOR'

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        scene = context.scene

        ALL_MT_editormenu.draw_hidden(context, layout) # bfa - show hide the editormenu

        layout.prop(st, "view_type", text="")

        SEQUENCER_MT_editor_menus.draw_collapsible(context, layout)

        layout.separator_spacer()

        if st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
            layout.prop(st, "display_mode", text="", icon_only=True)

        if st.view_type != 'SEQUENCER':
            layout.prop(st, "preview_channels", text="", icon_only=True)

        if st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}:
            gpd = context.gpencil_data
            tool_settings = context.tool_settings

            # Proportional editing
            if gpd and gpd.use_stroke_edit_mode:
                row = layout.row(align=True)
                row.prop(tool_settings, "use_proportional_edit", icon_only=True)
                if tool_settings.use_proportional_edit:
                    row.prop(tool_settings, "proportional_edit_falloff", icon_only=True)

# bfa - show hide the editormenu
class ALL_MT_editormenu(Menu):
    bl_label = ""

    def draw(self, context):
        self.draw_menus(self.layout, context)

    @staticmethod
    def draw_menus(layout, context):

        row = layout.row(align=True)
        row.template_header() # editor type menus

class SEQUENCER_MT_editor_menus(Menu):
    bl_idname = "SEQUENCER_MT_editor_menus"
    bl_label = ""

    def draw(self, context):
        layout = self.layout
        st = context.space_data

        layout.menu("SEQUENCER_MT_view")

        if st.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'}:
            layout.menu("SEQUENCER_MT_select")
            layout.menu("SEQUENCER_MT_marker")
            layout.menu("SEQUENCER_MT_add")
            layout.menu("SEQUENCER_MT_frame")
            layout.menu("SEQUENCER_MT_strip")


class SEQUENCER_MT_view_toggle(Menu):
    bl_label = "View Type"

    def draw(self, _context):
        layout = self.layout

        layout.operator("sequencer.view_toggle").type = 'SEQUENCER'
        layout.operator("sequencer.view_toggle").type = 'PREVIEW'
        layout.operator("sequencer.view_toggle").type = 'SEQUENCER_PREVIEW'


class SEQUENCER_MT_view_cache(Menu):
    bl_label = "Cache"

    def draw(self, context):
        layout = self.layout

        ed = context.scene.sequence_editor
        layout.prop(ed, "show_cache")
        layout.separator()

        col = layout.column()
        col.enabled = ed.show_cache

        col.prop(ed, "show_cache_final_out")
        col.prop(ed, "show_cache_raw")
        col.prop(ed, "show_cache_preprocessed")
        col.prop(ed, "show_cache_composite")


class SEQUENCER_MT_view(Menu):
    bl_label = "View"

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        is_preview = st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}
        is_sequencer_view = st.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'}

        if st.view_type == 'PREVIEW':
            # Specifying the REGION_PREVIEW context is needed in preview-only
            # mode, else the lookup for the shortcut will fail in
            # wm_keymap_item_find_props() (see #32595).
            layout.operator_context = 'INVOKE_REGION_PREVIEW'

        layout.prop(st, "show_region_ui")
        layout.operator_context = 'INVOKE_DEFAULT'

        if st.view_type == 'SEQUENCER':
            layout.prop(st, "show_backdrop", text="Preview as Backdrop")

        layout.separator()

        if is_sequencer_view:
            layout.operator_context = 'INVOKE_REGION_WIN'
            layout.operator("sequencer.view_all", text="View all Sequences", icon = "VIEWALL" )
            layout.operator("sequencer.view_selected", text = "View Selected", icon='VIEW_SELECTED')
            layout.operator("sequencer.view_frame", icon = "VIEW_FRAME" )
            layout.operator_context = 'INVOKE_DEFAULT'

            layout.separator()

            layout.operator("sequencer.refresh_all", icon='FILE_REFRESH', text="Refresh All")

            layout.separator()

        if is_preview:
            layout.operator_context = 'INVOKE_REGION_PREVIEW'
            layout.operator("sequencer.view_all_preview", text="Fit Preview in window")
            layout.operator("view2d.zoom_border", text = "Zoom")

            layout.separator()

            ratios = ((1, 8), (1, 4), (1, 2), (1, 1), (2, 1), (4, 1), (8, 1))

            for a, b in ratios:
                layout.operator(
                    "sequencer.view_zoom_ratio",
                    text=iface_("Zoom %d:%d") % (a, b),
                    translate=False,
                ).ratio = a / b

            layout.separator()

            layout.operator_context = 'INVOKE_DEFAULT'

            # # XXX, invokes in the header view
            # layout.operator("sequencer.view_ghost_border", text="Overlay Border")

        layout.operator("render.opengl", text="Sequence Render Image", icon='RENDER_STILL').sequencer = True
        props = layout.operator("render.opengl", text="Sequence Render Animation", icon='RENDER_ANIMATION')
        props.animation = True
        props.sequencer = True

        layout.separator()

        layout.menu("INFO_MT_area")


# Workaround to separate the tooltips
class SEQUENCER_MT_select_inverse(bpy.types.Operator):
    """Inverse\nInverts the current selection """      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "sequencer.select_all_inverse"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select Inverse"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):        # execute() is called by blender when running the operator.
        bpy.ops.sequencer.select_all(action = 'INVERT')
        return {'FINISHED'}

# Workaround to separate the tooltips
class SEQUENCER_MT_select_none(bpy.types.Operator):
    """None\nDeselects everything """      # blender will use this as a tooltip for menu items and buttons.
    bl_idname = "sequencer.select_all_none"        # unique identifier for buttons and menu items to reference.
    bl_label = "Select None"         # display name in the interface.
    bl_options = {'REGISTER', 'UNDO'}  # enable undo for the operator.

    def execute(self, context):        # execute() is called by blender when running the operator.
        bpy.ops.sequencer.select_all(action = 'DESELECT')
        return {'FINISHED'}


class SEQUENCER_MT_select(Menu):
    bl_label = "Select"

    def draw(self, _context):
        layout = self.layout

        layout.operator("sequencer.select_all", text="All", icon='SELECT_ALL').action = 'SELECT'
        layout.operator("sequencer.select_all_none", text="None", icon='SELECT_NONE') # bfa - separated tooltip
        layout.operator("sequencer.select_all_inverse", text="Inverse", icon='INVERSE') # bfa - separated tooltip

        layout.separator()

        layout.operator_menu_enum("sequencer.select_grouped", "type", text="Grouped")
        layout.operator("sequencer.select_linked")

        layout.separator()

        layout.operator("sequencer.select_active_side", text="Strips to the Left").side = 'LEFT'
        layout.operator("sequencer.select_active_side", text="Strips to the Right").side = 'RIGHT'
        props = layout.operator("sequencer.select", text="All Strips to the Left")
        props.left_right = 'LEFT'
        props.linked_time = True
        props = layout.operator("sequencer.select", text="All Strips to the Right")
        props.left_right = 'RIGHT'
        props.linked_time = True

        layout.separator()

        layout.operator("sequencer.select_handles", text="Surrounding Handles").side = 'BOTH'
        layout.operator("sequencer.select_handles", text="Left Handle").side = 'LEFT'
        layout.operator("sequencer.select_handles", text="Right Handle").side = 'RIGHT'

        layout.separator()
        
        layout.operator("sequencer.select_less", text = "Less")
        layout.operator("sequencer.select_more", text = "More")


class SEQUENCER_MT_marker(Menu):
    bl_label = "Marker"

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        is_sequencer_view = st.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'}

        from bl_ui.space_time import marker_menu_generic
        marker_menu_generic(layout, context)

        if is_sequencer_view:
            layout.prop(st, "use_marker_sync")


class SEQUENCER_MT_change(Menu):
    bl_label = "Change"

    def draw(self, context):
        layout = self.layout
        strip = act_strip(context)

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.operator_menu_enum("sequencer.change_effect_input", "swap")
        layout.operator_menu_enum("sequencer.change_effect_type", "type")
        prop = layout.operator("sequencer.change_path", text="Path/Files")

        if strip:
            strip_type = strip.type

            if strip_type == 'IMAGE':
                prop.filter_image = True
            elif strip_type == 'MOVIE':
                prop.filter_movie = True
            elif strip_type == 'SOUND':
                prop.filter_sound = True


class SEQUENCER_MT_frame(Menu):
    bl_label = "Frame"

    def draw(self, _context):
        layout = self.layout

        layout.operator("anim.previewrange_clear")
        layout.operator("anim.previewrange_set")

        layout.separator()

        props = layout.operator("sequencer.strip_jump", text="Jump to Previous Strip")
        props.next = False
        props.center = False
        props = layout.operator("sequencer.strip_jump", text="Jump to Next Strip")
        props.next = True
        props.center = False

        layout.separator()

        props = layout.operator("sequencer.strip_jump", text="Jump to Previous Strip (Center)")
        props.next = False
        props.center = True
        props = layout.operator("sequencer.strip_jump", text="Jump to Next Strip (Center)")
        props.next = True
        props.center = True


class SEQUENCER_MT_add(Menu):
    bl_label = "Add"
    bl_translation_context = i18n_contexts.operator_default

    def draw(self, context):

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        bpy_data_scenes_len = len(bpy.data.scenes)
        if bpy_data_scenes_len > 10:
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("sequencer.scene_strip_add", text="Scene...", icon='SCENE_DATA')
        elif bpy_data_scenes_len > 1:
            layout.operator_menu_enum("sequencer.scene_strip_add", "scene", text="Scene", icon='SCENE_DATA')
        else:
            layout.menu("SEQUENCER_MT_add_empty", text="Scene", icon='SCENE_DATA')
        del bpy_data_scenes_len

        bpy_data_movieclips_len = len(bpy.data.movieclips)
        if bpy_data_movieclips_len > 10:
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("sequencer.movieclip_strip_add", text="Clip...", icon='TRACKER')
        elif bpy_data_movieclips_len > 0:
            layout.operator_menu_enum("sequencer.movieclip_strip_add", "clip", text="Clip", icon='TRACKER')
        else:
            layout.menu("SEQUENCER_MT_add_empty", text="Clip", icon='TRACKER')
        del bpy_data_movieclips_len

        bpy_data_masks_len = len(bpy.data.masks)
        if bpy_data_masks_len > 10:
            layout.operator_context = 'INVOKE_DEFAULT'
            layout.operator("sequencer.mask_strip_add", text="Mask...", icon='MOD_MASK')
        elif bpy_data_masks_len > 0:
            layout.operator_menu_enum("sequencer.mask_strip_add", "mask", text="Mask", icon='MOD_MASK')
        else:
            layout.menu("SEQUENCER_MT_add_empty", text="Mask", icon='MOD_MASK')
        del bpy_data_masks_len

        layout.separator()

        layout.operator("sequencer.movie_strip_add", text="Movie", icon='FILE_MOVIE')
        layout.operator("sequencer.sound_strip_add", text="Sound", icon='FILE_SOUND')
        layout.operator("sequencer.image_strip_add", text="Image/Sequence", icon='FILE_IMAGE')

        layout.separator()

        layout.operator_context = 'INVOKE_REGION_WIN'
        layout.operator("sequencer.effect_strip_add", text="Color", icon='COLOR').type = 'COLOR'
        layout.operator("sequencer.effect_strip_add", text="Text", icon='FONT_DATA').type = 'TEXT'

        layout.separator()

        layout.operator("sequencer.effect_strip_add", text="Adjustment Layer", icon='COLOR').type = 'ADJUSTMENT'

        layout.operator_context = 'INVOKE_DEFAULT'
        layout.menu("SEQUENCER_MT_add_effect", icon='SHADERFX')

        col = layout.column()
        col.menu("SEQUENCER_MT_add_transitions", icon='ARROW_LEFTRIGHT')
        col.enabled = selected_sequences_len(context) >= 2


class SEQUENCER_MT_add_empty(Menu):
    bl_label = "Empty"

    def draw(self, _context):
        layout = self.layout

        layout.label(text="No Items Available")


class SEQUENCER_MT_add_transitions(Menu):
    bl_label = "Transitions"

    def draw(self, context):

        layout = self.layout

        col = layout.column()

        col.operator("sequencer.crossfade_sounds", text="Sound Crossfade", icon='SPEAKER')

        col.separator()

        col.operator("sequencer.effect_strip_add", text="Cross", icon='NODE_VECTOR').type = 'CROSS'
        col.operator("sequencer.effect_strip_add", text="Gamma Cross", icon='NODE_GAMMA').type = 'GAMMA_CROSS'

        col.separator()

        col.operator("sequencer.effect_strip_add", text="Wipe", icon='NODE_VECTOR_TRANSFORM').type = 'WIPE'
        col.enabled = selected_sequences_len(context) >= 2


class SEQUENCER_MT_add_effect(Menu):
    bl_label = "Effect Strip"

    def draw(self, context):

        layout = self.layout
        layout.operator_context = 'INVOKE_REGION_WIN'

        col = layout.column()
        col.operator("sequencer.effect_strip_add", text="Add", icon='SEQ_ADD').type = 'ADD'
        col.operator("sequencer.effect_strip_add", text="Subtract", icon='NODE_INVERT').type = 'SUBTRACT'
        col.operator("sequencer.effect_strip_add", text="Multiply", icon='SEQ_MULTIPLY').type = 'MULTIPLY'
        col.operator("sequencer.effect_strip_add", text="Over Drop", icon='SEQ_ALPHA_OVER').type = 'OVER_DROP'
        col.operator("sequencer.effect_strip_add", text="Alpha Over", icon='IMAGE_ALPHA').type = 'ALPHA_OVER'
        col.operator("sequencer.effect_strip_add", text="Alpha Under", icon='NODE_HOLDOUTSHADER').type = 'ALPHA_UNDER'
        col.operator("sequencer.effect_strip_add", text="Color Mix", icon='NODE_MIXRGB').type = 'COLORMIX'
        col.enabled = selected_sequences_len(context) >= 2

        layout.separator()

        layout.operator("sequencer.effect_strip_add", text="Multicam Selector", icon='SEQ_MULTICAM').type = 'MULTICAM'

        layout.separator()

        col = layout.column()
        col.operator("sequencer.effect_strip_add", text="Transform", icon='TRANSFORM_MOVE').type = 'TRANSFORM'
        col.operator("sequencer.effect_strip_add", text="Speed Control", icon='NODE_CURVE_TIME').type = 'SPEED'

        col.separator()

        col.operator("sequencer.effect_strip_add", text="Glow", icon='LAMP_SUN').type = 'GLOW'
        col.operator("sequencer.effect_strip_add", text="Gaussian Blur", icon='NODE_BLUR').type = 'GAUSSIAN_BLUR'
        col.enabled = selected_sequences_len(context) != 0


class SEQUENCER_MT_strip_transform(Menu):
    bl_label = "Transform"

    def draw(self, _context):
        layout = self.layout

        layout.operator("transform.transform", text="Move", icon = "TRANSFORM_MOVE").mode = 'TRANSLATION'
        layout.operator("transform.transform", text="Move/Extend from Playhead", icon = "SEQ_MOVE_EXTEND").mode = 'TIME_EXTEND'
        layout.operator("sequencer.slip", text="Slip Strip Contents", icon = "SEQ_SLIP_CONTENTS")

        layout.separator()
        layout.operator("sequencer.snap", icon = "SEQ_SNAP_STRIP")
        layout.operator("sequencer.offset_clear", icon = "SEQ_CLEAR_OFFSET")

        layout.separator()
        layout.operator("sequencer.swap", text="Swap Strip Left", icon = "SEQ_SWAP_LEFT").side = 'LEFT'
        layout.operator("sequencer.swap", text="Swap Strip Right", icon = "SEQ_SWAP_RIGHT").side = 'RIGHT'

        layout.separator()
        layout.operator("sequencer.gap_remove", icon = "SEQ_REMOVE_GAPS").all = False
        layout.operator("sequencer.gap_insert", icon = "SEQ_INSERT_GAPS")


class SEQUENCER_MT_strip_input(Menu):
    bl_label = "Inputs"

    def draw(self, context):
        layout = self.layout
        strip = act_strip(context)

        layout.operator("sequencer.reload", text="Reload Strips", icon = "SEQ_RELOAD_STRIPS")
        layout.operator("sequencer.reload", text="Reload Strips and Adjust Length", icon = "SEQ_RELOAD_ADJUST_LENGTH").adjust_length = True
        prop = layout.operator("sequencer.change_path", text="Change Path/Files", icon = "FILE_MOVIE")
        layout.operator("sequencer.swap_data", text="Swap Data", icon = "SEQ_SWAP_DATA")

        if strip:
            strip_type = strip.type

            if strip_type == 'IMAGE':
                prop.filter_image = True
            elif strip_type == 'MOVIE':
                prop.filter_movie = True
            elif strip_type == 'SOUND':
                prop.filter_sound = True



class SEQUENCER_MT_strip_lock_mute(Menu):
    bl_label = "Lock/Mute"

    def draw(self, _context):
        layout = self.layout

        layout.operator("sequencer.lock", icon='LOCKED')
        layout.operator("sequencer.unlock", icon='UNLOCKED')

        layout.separator()

        layout.operator("sequencer.mute", icon='RESTRICT_VIEW_ON').unselected = False
        layout.operator("sequencer.unmute", icon='RESTRICT_VIEW_OFF').unselected = False
        layout.operator("sequencer.mute", text="Mute Unselected Strips", icon='HIDE_UNSELECTED').unselected = True
        layout.operator("sequencer.unmute", text="Unmute Deselected Strips", icon='SHOW_UNSELECTED').unselected = True




class SEQUENCER_MT_strip(Menu):
    bl_label = "Strip"

    def draw(self, context):
        layout = self.layout

        layout.operator_context = 'INVOKE_REGION_WIN'

        layout.separator()
        layout.menu("SEQUENCER_MT_strip_transform")
        layout.operator("sequencer.snap")
        layout.operator("sequencer.offset_clear")

        layout.separator()
        layout.operator("sequencer.copy", text="Copy", icon='COPYDOWN')
        layout.operator("sequencer.paste", text="Paste", icon='PASTEDOWN')
        layout.operator("sequencer.duplicate_move", icon='DUPLICATE')
        layout.operator("sequencer.delete", text="Delete...", icon='DELETE')

        layout.separator()
        layout.operator("sequencer.cut", text="Cut (Hard) at Playhead", icon='SEQ_CUT_HARD_AT_FRAME').type = 'HARD'
        layout.operator("sequencer.cut", text="Cut (Soft) at Playhead", icon='SEQ_CUT_SOFT_AT_FRAME').type = 'SOFT'

        layout.separator()
        layout.operator("sequencer.deinterlace_selected_movies")
        layout.operator("sequencer.rebuild_proxy")

        strip = act_strip(context)

        if strip:
            strip_type = strip.type

            if strip_type != 'SOUND':
                layout.separator()
                layout.operator_menu_enum("sequencer.strip_modifier_add", "type", text="Add Strip Modifier")
                layout.operator("sequencer.strip_modifier_copy", text="Copy Modifiers to Selection", icon='COPYDOWN')

            if strip_type in {
                    'CROSS', 'ADD', 'SUBTRACT', 'ALPHA_OVER', 'ALPHA_UNDER',
                    'GAMMA_CROSS', 'MULTIPLY', 'OVER_DROP', 'WIPE', 'GLOW',
                    'TRANSFORM', 'COLOR', 'SPEED', 'MULTICAM', 'ADJUSTMENT',
                    'GAUSSIAN_BLUR', 'TEXT',
            }:
                layout.separator()
                layout.menu("SEQUENCER_MT_strip_effect")
            elif strip_type == 'MOVIE':
                layout.separator()
                layout.menu("SEQUENCER_MT_strip_movie")
            elif strip_type == 'IMAGE':
                layout.separator()
                layout.operator("sequencer.rendersize")
                layout.operator("sequencer.images_separate")
            elif strip_type == 'META':
                layout.separator()
                layout.operator("sequencer.meta_make")
                layout.operator("sequencer.meta_separate")
                layout.operator("sequencer.meta_toggle", text="Toggle Meta")
            if strip_type != 'META':
                layout.separator()
                layout.operator("sequencer.meta_make")
                layout.operator("sequencer.meta_toggle", text="Toggle Meta")

        layout.separator()
        layout.menu("SEQUENCER_MT_strip_lock_mute")

        layout.separator()
        layout.menu("SEQUENCER_MT_strip_input")

        layout.separator()
        layout.menu("SEQUENCER_MT_strip_lock_mute")


class SequencerButtonsPanel:
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    @staticmethod
    def has_sequencer(context):
        return (context.space_data.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'})

    @classmethod
    def poll(cls, context):
        return cls.has_sequencer(context) and (act_strip(context) is not None)


class SequencerButtonsPanel_Output:
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    @staticmethod
    def has_preview(context):
        st = context.space_data
        return (st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}) or st.show_backdrop

    @classmethod
    def poll(cls, context):
        return cls.has_preview(context)


class SEQUENCER_PT_edit(SequencerButtonsPanel, Panel):
    bl_label = "Edit Strip"
    bl_category = "Strip"

    def draw(self, context):
        layout = self.layout

        scene = context.scene
        frame_current = scene.frame_current
        strip = act_strip(context)

        split = layout.split(factor=0.25)
        split.label(text="Name:")
        split.prop(strip, "name", text="")

        split = layout.split(factor=0.25)
        split.label(text="Type:")
        split.prop(strip, "type", text="")

        if strip_type != 'SOUND':
            split = layout.split(factor=0.25)
            split.label(text="Blend:")
            split.prop(strip, "blend_type", text="")

            row = layout.row(align=True)
            sub = row.row(align=True)
            sub.active = (not strip.mute)
            sub.prop(strip, "blend_alpha", text="Opacity", slider=True)
            row.prop(strip, "mute", toggle=True, icon_only=True)

        else:
            row = layout.row()
            row.prop(strip, "mute", toggle=True, icon_only=True, icon='MUTE_IPO_OFF')

        col = layout.column(align=True)
        row = col.row(align=True)

        row_sub = row.row(align=True)
        row_sub.enabled = not strip.lock
        row_sub.prop(strip, "channel")
        row.prop(strip, "lock", toggle=True, icon_only=True)

        sub = col.column(align=True)
        sub.enabled = not strip.lock
        sub.prop(strip, "frame_start")
        sub.prop(strip, "frame_final_duration")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.label(text=iface_("Final Length: %s") % bpy.utils.smpte_from_frame(strip.frame_final_duration),
                  translate=False)
        row = col.row(align=True)
        row.active = strip.frame_start <= frame_current <= strip.frame_start + strip.frame_duration
        row.label(text=iface_("Playhead: %d") % (frame_current - strip.frame_start), translate=False)

        col.label(text=iface_("Frame Offset %d:%d") % (strip.frame_offset_start, strip.frame_offset_end),
                  translate=False)
        col.label(text=iface_("Frame Still %d:%d") % (strip.frame_still_start, strip.frame_still_end), translate=False)

        elem = False

        if strip.type == 'IMAGE':
            elem = strip.strip_elem_from_frame(frame_current)
        elif strip.type == 'MOVIE':
            elem = strip.elements[0]

        if elem and elem.orig_width > 0 and elem.orig_height > 0:
            col.label(text=iface_("Original Dimension: %dx%d") % (elem.orig_width, elem.orig_height), translate=False)
        else:
            col.label(text="Original Dimension: None")


class SEQUENCER_PT_effect(SequencerButtonsPanel, Panel):
    bl_label = "Effect Strip"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return strip.type in {
            'ADD', 'SUBTRACT', 'ALPHA_OVER', 'ALPHA_UNDER',
            'CROSS', 'GAMMA_CROSS', 'MULTIPLY', 'OVER_DROP',
            'WIPE', 'GLOW', 'TRANSFORM', 'COLOR', 'SPEED',
            'MULTICAM', 'GAUSSIAN_BLUR', 'TEXT', 'COLORMIX'
        }

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        strip = act_strip(context)

        layout.active = not strip.mute

        if strip.input_count > 0:
            col = layout.column()
            col.enabled = False
            col.prop(strip, "input_1")
            if strip.input_count > 1:
                col.prop(strip, "input_2")

        strip_type = strip.type

        if strip_type == 'COLOR':
            layout.prop(strip, "color")

        elif strip_type == 'WIPE':
            col = layout.column()
            col.prop(strip, "transition_type")
            col.alignment = 'RIGHT'
            col.row().prop(strip, "direction", expand=True)

            col = layout.column()
            col.prop(strip, "blur_width", slider=True)
            if strip.transition_type in {'SINGLE', 'DOUBLE'}:
                col.prop(strip, "angle")

        elif strip_type == 'GLOW':
            flow = layout.column_flow()
            flow.prop(strip, "threshold", slider=True)
            flow.prop(strip, "clamp", slider=True)
            flow.prop(strip, "boost_factor")
            flow.prop(strip, "blur_radius")

            row = layout.row()
            row.prop(strip, "quality", slider=True)
            row.prop(strip, "use_only_boost")

        elif strip_type == 'SPEED':
            layout.prop(strip, "use_default_fade", text="Stretch to input strip length")
            if not strip.use_default_fade:
                layout.prop(strip, "use_as_speed")
                if strip.use_as_speed:
                    layout.prop(strip, "speed_factor")
                else:
                    layout.prop(strip, "speed_factor", text="Frame Number")
                    layout.prop(strip, "use_scale_to_length")

        elif strip_type == 'TRANSFORM':
            col = layout.column()

            col.prop(strip, "interpolation")
            col.prop(strip, "translation_unit")
            col = layout.column(align=True)
            col.prop(strip, "translate_start_x", text="Position X")
            col.prop(strip, "translate_start_y", text="Y")

            col.separator()

            colsub = col.column(align=True)
            colsub.prop(strip, "use_uniform_scale")
            if strip.use_uniform_scale:
                colsub = col.column(align=True)
                colsub.prop(strip, "scale_start_x", text="Scale")
            else:
                col.prop(strip, "scale_start_x", text="Scale X")
                col.prop(strip, "scale_start_y", text="Y")

            col.separator()

            col = layout.column(align=True)
            col.label(text="Rotation:")
            col.prop(strip, "rotation_start", text="Rotation")

        elif strip_type == 'MULTICAM':
            col = layout.column(align=True)
            strip_channel = strip.channel

            col.prop(strip, "multicam_source", text="Source Channel")

            # The multicam strip needs at least 2 strips to be useful
            if strip_channel > 2:
                BT_ROW = 4
                col.label(text="Cut to")
                row = col.row()

                for i in range(1, strip_channel):
                    if (i % BT_ROW) == 1:
                        row = col.row(align=True)

                    # Workaround - .enabled has to have a separate UI block to work
                    if i == strip.multicam_source:
                        sub = row.row(align=True)
                        sub.enabled = False
                        sub.operator("sequencer.cut_multicam", text=f"{i:d}").camera = i
                    else:
                        sub_1 = row.row(align=True)
                        sub_1.enabled = True
                        sub_1.operator("sequencer.cut_multicam", text=f"{i:d}").camera = i

                if strip.channel > BT_ROW and (strip_channel - 1) % BT_ROW:
                    for i in range(strip.channel, strip_channel + ((BT_ROW + 1 - strip_channel) % BT_ROW)):
                        row.label(text="")
            else:
                col.separator()
                col.label(text="Two or more channels are needed below this strip", icon='INFO')

        elif strip_type == 'TEXT':
            col = layout.column()
            col.prop(strip, "text")
            col.template_ID(strip, "font", open="font.open", unlink="font.unlink")
            col.prop(strip, "font_size")

            row = col.row()
            row.prop(strip, "color")
            row = col.row()
            row.prop(strip, "use_shadow")
            rowsub = row.row()
            rowsub.active = strip.use_shadow
            rowsub.prop(strip, "shadow_color", text="")

            col.prop(strip, "align_x", text="Horizontal")
            col.prop(strip, "align_y", text="Vertical")
            row = col.row(align=True)
            row.prop(strip, "location", text="Location", slider=True)
            col.prop(strip, "wrap_width")

            layout.operator("sequencer.export_subtitles", text="Export Subtitles", icon='EXPORT')

        col = layout.column(align=True)
        if strip_type == 'SPEED':
            col.prop(strip, "multiply_speed")
        elif strip_type in {'CROSS', 'GAMMA_CROSS', 'WIPE', 'ALPHA_OVER', 'ALPHA_UNDER', 'OVER_DROP'}:
            col.prop(strip, "use_default_fade", text="Default fade")
            if not strip.use_default_fade:
                col.prop(strip, "effect_fader", text="Effect Fader")
        elif strip_type == 'GAUSSIAN_BLUR':
            col = layout.column(align=True)
            col.prop(strip, "size_x", text="Size X")
            col.prop(strip, "size_y", text="Y")
        elif strip_type == 'COLORMIX':
            layout.prop(strip, "blend_effect", text="Blend Mode")
            row = layout.row(align=True)
            row.prop(strip, "factor", slider=True)


class SEQUENCER_PT_input(SequencerButtonsPanel, Panel):
    bl_label = "Strip Input"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return strip.type in {
            'MOVIE', 'IMAGE', 'SCENE', 'MOVIECLIP', 'META',
            'ADD', 'SUBTRACT', 'ALPHA_OVER', 'ALPHA_UNDER',
            'CROSS', 'GAMMA_CROSS', 'MULTIPLY', 'OVER_DROP',
            'WIPE', 'GLOW', 'TRANSFORM', 'COLOR',
            'MULTICAM', 'SPEED', 'ADJUSTMENT', 'COLORMIX'
        }

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        scene = context.scene

        strip = act_strip(context)
        strip_type = strip.type

        seq_type = strip.type

        # draw a filename if we have one
        if seq_type == 'IMAGE':
            split = layout.split(factor=0.2)
            split.label(text="Path:")
            split.prop(strip, "directory", text="")

            # Current element for the filename

            elem = strip.strip_elem_from_frame(scene.frame_current)
            if elem:
                split = layout.split(factor=0.2)
                split.label(text="File:")
                split.prop(elem, "filename", text="")  # strip.elements[0] could be a fallback

            split = layout.split(factor=0.4)
            split.label(text="Color Space:")
            split.prop(strip.colorspace_settings, "name", text="")

            split = layout.split(factor=0.4)
            split.label(text="Alpha:")
            split.prop(strip, "alpha_mode", text="")

            layout.operator("sequencer.change_path", icon='FILEBROWSER').filter_image = True

        elif seq_type == 'MOVIE':
            split = layout.split(factor=0.2)
            split.label(text="Path:")
            split.prop(strip, "filepath", text="")

            split = layout.split(factor=0.4)
            split.label(text="Color Space:")
            split.prop(strip.colorspace_settings, "name", text="")

            layout.prop(strip, "mpeg_preseek")
            layout.prop(strip, "stream_index")

        layout.prop(strip, "use_translation", text="Image Offset")
        if strip.use_translation:
            row = layout.row(align=True)
            row.prop(strip.transform, "offset_x", text="X")
            row.prop(strip.transform, "offset_y", text="Y")

        layout.prop(strip, "use_crop", text="Image Crop")
        if strip.use_crop:
            col = layout.column(align=True)
            col.prop(strip.crop, "max_y")
            row = col.row(align=True)
            row.prop(strip.crop, "min_x")
            row.prop(strip.crop, "max_x")
            col.prop(strip.crop, "min_y")

            box = col.box()
            box.active = strip.views_format == 'STEREO_3D'
            box.template_image_stereo_3d(strip.stereo_3d_format)

            # Resolution.
            col = layout.column(align=True)
            col = col.box()
            split = col.split(factor=0.5, align=False)
            split.alignment = 'RIGHT'
            split.label(text="Resolution")
            size = (elem.orig_width, elem.orig_height) if elem else (0, 0)
            if size[0] and size[1]:
                split.alignment = 'LEFT'
                split.label(text="%dx%d" % size, translate=False)
            else:
                split.label(text="None")


class SEQUENCER_PT_sound(SequencerButtonsPanel, Panel):
    bl_label = "Sound"
    bl_parent_id = ""
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return (strip.type == 'SOUND')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        st = context.space_data
        strip = act_strip(context)
        sound = strip.sound

        layout.active = not strip.mute

        layout.template_ID(strip, "sound", open="sound.open")
        if sound is not None:
            layout.prop(sound, "filepath", text="")

            row = layout.row()
            if sound.packed_file:
                row.operator("sound.unpack", icon='PACKAGE', text="Unpack")
            else:
                row.operator("sound.pack", icon='UGLYPACKAGE', text="Pack")

            row.prop(sound, "use_memory_cache")

            layout.prop(sound, "use_mono")

        if st.waveform_display_type == 'DEFAULT_WAVEFORMS':
            layout.prop(strip, "show_waveform")

        col = layout.column(align=True)
        col.prop(strip, "volume")
        col.prop(strip, "pitch")
        col.prop(strip, "pan")

        col = layout.column(align=True)
        col.label(text="Trim Duration (hard):")
        row = layout.row(align=True)
        row.prop(strip, "animation_offset_start", text="Start")
        row.prop(strip, "animation_offset_end", text="End")

        col = layout.column(align=True)
        col.label(text="Trim Duration (soft):")
        row = layout.row(align=True)
        row.prop(strip, "frame_offset_start", text="Start")
        row.prop(strip, "frame_offset_end", text="End")


class SEQUENCER_PT_scene(SequencerButtonsPanel, Panel):
    bl_label = "Scene"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return (strip.type == 'SCENE')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        strip = act_strip(context)

        layout.active = not strip.mute

        layout.template_ID(strip, "scene")

        scene = strip.scene
        layout.prop(strip, "scene_input")

        if scene:
            layout.prop(scene, "audio_volume", text="Volume")

        if strip.scene_input == 'CAMERA':
            layout.alignment = 'RIGHT'
            sub = layout.column(align=True)
            split = sub.split(factor=0.5, align=True)
            split.alignment = 'RIGHT'
            split.label(text="Camera")
            split.template_ID(strip, "scene_camera")

            layout.prop(strip, "use_grease_pencil", text="Show Grease Pencil")

        if scene:
            layout.prop(scene, "audio_volume", text="Audio Volume")

        if not strip.use_sequence:
            if scene:
                # Warning, this is not a good convention to follow.
                # Expose here because setting the alpha from the 'Render' menu is very inconvenient.
                layout.label(text="Preview")
                layout.prop(scene.render, "alpha_mode")

        if scene:
            sta = scene.frame_start
            end = scene.frame_end
            layout.label(text=iface_("Original frame range: %d-%d (%d)") % (sta, end, end - sta + 1), translate=False)


class SEQUENCER_PT_mask(SequencerButtonsPanel, Panel):
    bl_label = "Mask"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return (strip.type == 'MASK')

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        strip = act_strip(context)

        layout.active = not strip.mute

        layout.template_ID(strip, "mask")

        mask = strip.mask

        if mask:
            sta = mask.frame_start
            end = mask.frame_end
            layout.label(text=iface_("Original frame range: %d-%d (%d)") % (sta, end, end - sta + 1), translate=False)


class SEQUENCER_PT_filter(SequencerButtonsPanel, Panel):
    bl_label = "Filter"
    bl_category = "Strip"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return strip.type in {
            'MOVIE', 'IMAGE', 'SCENE', 'MOVIECLIP', 'MASK',
            'META', 'ADD', 'SUBTRACT', 'ALPHA_OVER',
            'ALPHA_UNDER', 'CROSS', 'GAMMA_CROSS', 'MULTIPLY',
            'OVER_DROP', 'WIPE', 'GLOW', 'TRANSFORM', 'COLOR',
            'MULTICAM', 'SPEED', 'ADJUSTMENT', 'COLORMIX'
        }

    def draw(self, context):
        layout = self.layout

        strip = act_strip(context)

        col = layout.column()
        col.label(text="Video:")
        col.prop(strip, "strobe")

        if strip.type == 'MOVIECLIP':
            col = layout.column()
            col.label(text="Tracker")
            col.prop(strip, "stabilize2d")

            col = layout.column()
            col.label(text="Distortion")
            col.prop(strip, "undistort")
            col.separator()

        split = layout.split(factor=0.6)
        col = split.column()
        col.prop(strip, "use_reverse_frames", text="Reverse")
        col.prop(strip, "use_deinterlace")

        col = split.column()
        col.prop(strip, "use_flip_x", text="X Flip")
        col.prop(strip, "use_flip_y", text="Y Flip")

        layout.label(text="Color:")
        col = layout.column(align=True)
        col.prop(strip, "color_saturation", text="Saturation")
        col.prop(strip, "color_multiply", text="Multiply")
        col.prop(strip, "use_float", text="Convert to Float")


class SEQUENCER_PT_cache_settings(SequencerButtonsPanel, Panel):
    bl_label = "Cache Settings"
    bl_category = "Proxy & Cache"

    @classmethod
    def poll(cls, context):
        return cls.has_sequencer(context) and context.scene.sequence_editor

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        ed = context.scene.sequence_editor

        col = layout.column()

        col.prop(ed, "use_cache_raw")
        col.prop(ed, "use_cache_preprocessed")
        col.prop(ed, "use_cache_composite")
        col.prop(ed, "use_cache_final")
        col.separator()
        col.prop(ed, "recycle_max_cost")


class SEQUENCER_PT_proxy_settings(SequencerButtonsPanel, Panel):
    bl_label = "Proxy Settings"
    bl_category = "Proxy & Cache"

    @classmethod
    def poll(cls, context):
        return cls.has_sequencer(context) and context.scene.sequence_editor

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        ed = context.scene.sequence_editor
        flow = layout.column_flow()
        flow.prop(ed, "proxy_storage", text="Storage")

        if ed.proxy_storage == 'PROJECT':
            flow.prop(ed, "proxy_dir", text="Directory")

        col = layout.column()
        col.operator("sequencer.enable_proxies")
        col.operator("sequencer.rebuild_proxy", icon='LASTOPERATOR')


class SEQUENCER_PT_strip_proxy(SequencerButtonsPanel, Panel):
    bl_label = "Strip Proxy & Timecode"
    bl_category = "Proxy & Cache"

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context) and context.scene.sequence_editor:
            return False

        strip = act_strip(context)
        if not strip:
            return False

        return strip.type in {'MOVIE', 'IMAGE', 'SCENE', 'META', 'MULTICAM'}

    def draw_header(self, context):
        strip = act_strip(context)

        self.layout.prop(strip, "use_proxy", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        ed = context.scene.sequence_editor

        strip = act_strip(context)

        if strip.proxy:
            proxy = strip.proxy

            flow = layout.column_flow()
            if ed.proxy_storage == 'PER_STRIP':
                flow.prop(proxy, "use_proxy_custom_directory")
                flow.prop(proxy, "use_proxy_custom_file")

                if proxy.use_proxy_custom_directory and not proxy.use_proxy_custom_file:
                    flow.prop(proxy, "directory")
                if proxy.use_proxy_custom_file:
                    flow.prop(proxy, "filepath")

            box = layout.box()
            row = box.row(align=True)
            row.prop(strip.proxy, "build_25")
            row.prop(strip.proxy, "build_75")
            row = box.row(align=True)
            row.prop(strip.proxy, "build_50")
            row.prop(strip.proxy, "build_100")

            layout.use_property_split = True
            layout.use_property_decorate = False

            layout.prop(proxy, "use_overwrite")

            col = layout.column()
            col.prop(proxy, "quality", text="Build JPEG Quality")

            if strip.type == 'MOVIE':
                col = layout.column()

                col.prop(proxy, "timecode", text="Timecode Index")


class SEQUENCER_PT_strip_cache(SequencerButtonsPanel, Panel):
    bl_label = "Strip Cache"
    bl_category = "Proxy & Cache"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if not cls.has_sequencer(context):
            return False
        if act_strip(context) is not None:
            return True
        return False

    def draw_header(self, context):
        strip = act_strip(context)
        self.layout.prop(strip, "override_cache_settings", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        strip = act_strip(context)
        layout.active = strip.override_cache_settings

        col = layout.column()
        col.prop(strip, "use_cache_raw")
        col.prop(strip, "use_cache_preprocessed")
        col.prop(strip, "use_cache_composite")

class SEQUENCER_PT_preview(SequencerButtonsPanel_Output, Panel):
    bl_label = "Scene Preview/Render"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "View"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        render = context.scene.render

        col = layout.column()
        col.prop(render, "sequencer_gl_preview", text="Preview Shading")

        if render.sequencer_gl_preview in ['SOLID', 'WIREFRAME']:
            col.prop(render, "use_sequencer_override_scene_strip")


class SEQUENCER_PT_view(SequencerButtonsPanel_Output, Panel):
    bl_label = "View Settings"
    bl_category = "View"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        st = context.space_data

        col = layout.column()
        col.prop(st, "display_channel", text="Channel")

        if st.display_mode == 'IMAGE':
            col.prop(st, "show_overexposed")

        elif st.display_mode == 'WAVEFORM':
            col.prop(st, "show_separate_color")

        col.prop(st, "proxy_render_size")


class SEQUENCER_PT_view_safe_areas(SequencerButtonsPanel_Output, Panel):
    bl_label = "Safe Areas"
    bl_options = {'DEFAULT_CLOSED'}
    bl_category = "View"

    @classmethod
    def poll(cls, context):
        st = context.space_data
        is_preview = st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}
        return is_preview and (st.display_mode == 'IMAGE')

    def draw_header(self, context):
        st = context.space_data

        self.layout.prop(st, "show_safe_areas", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        st = context.space_data
        safe_data = context.scene.safe_areas

        draw_display_safe_settings(layout, safe_data, st)


class SEQUENCER_PT_modifiers(SequencerButtonsPanel, Panel):
    bl_label = "Modifiers"
    bl_category = "Modifiers"

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True

        strip = act_strip(context)
        ed = context.scene.sequence_editor

        layout.prop(strip, "use_linear_modifiers")

        layout.operator_menu_enum("sequencer.strip_modifier_add", "type")
        layout.operator("sequencer.strip_modifier_copy", icon='ICON_COPYDOWN')

        for mod in strip.modifiers:
            box = layout.box()

            row = box.row()
            row.prop(mod, "show_expanded", text="", emboss=False)
            row.prop(mod, "name", text="")

            row.prop(mod, "mute", text="")

            sub = row.row(align=True)
            props = sub.operator("sequencer.strip_modifier_move", text="", icon='TRIA_UP')
            props.name = mod.name
            props.direction = 'UP'
            props = sub.operator("sequencer.strip_modifier_move", text="", icon='TRIA_DOWN')
            props.name = mod.name
            props.direction = 'DOWN'

            row.operator("sequencer.strip_modifier_remove", text="", icon='X', emboss=False).name = mod.name

            if mod.show_expanded:
                row = box.row()
                row.prop(mod, "input_mask_type", expand=True)

                if mod.input_mask_type == 'STRIP':
                    sequences_object = ed
                    if ed.meta_stack:
                        sequences_object = ed.meta_stack[-1]
                    box.prop_search(mod, "input_mask_strip", sequences_object, "sequences", text="Mask")
                else:
                    box.prop(mod, "input_mask_id")
                    row = box.row()
                    row.prop(mod, "mask_time", expand=True)

                if mod.type == 'COLOR_BALANCE':
                    box.prop(mod, "color_multiply")
                    draw_color_balance(box, mod.color_balance)
                elif mod.type == 'CURVES':
                    box.template_curve_mapping(mod, "curve_mapping", type='COLOR', show_tone=True)
                elif mod.type == 'HUE_CORRECT':
                    box.template_curve_mapping(mod, "curve_mapping", type='HUE')
                elif mod.type == 'BRIGHT_CONTRAST':
                    col = box.column()
                    col.prop(mod, "bright")
                    col.prop(mod, "contrast")
                elif mod.type == 'WHITE_BALANCE':
                    col = box.column()
                    col.prop(mod, "white_value")
                elif mod.type == 'TONEMAP':
                    col = box.column()
                    col.prop(mod, "tonemap_type")
                    if mod.tonemap_type == 'RD_PHOTORECEPTOR':
                        col.prop(mod, "intensity")
                        col.prop(mod, "contrast")
                        col.prop(mod, "adaptation")
                        col.prop(mod, "correction")
                    elif mod.tonemap_type == 'RH_SIMPLE':
                        col.prop(mod, "key")
                        col.prop(mod, "offset")
                        col.prop(mod, "gamma")


class SEQUENCER_PT_grease_pencil(AnnotationDataPanel, SequencerButtonsPanel_Output, Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "View"

    # NOTE: this is just a wrapper around the generic GP Panel
    # But, it should only show up when there are images in the preview region


class SEQUENCER_PT_grease_pencil_tools(GreasePencilToolsPanel, SequencerButtonsPanel_Output, Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "View"

    # NOTE: this is just a wrapper around the generic GP tools panel
    # It contains access to some essential tools usually found only in
    # toolbar, which doesn't exist here...


class SEQUENCER_PT_custom_props(SequencerButtonsPanel, PropertyPanel, Panel):
    COMPAT_ENGINES = {'BLENDER_RENDER', 'BLENDER_EEVEE', 'BLENDER_WORKBENCH'}
    _context_path = "scene.sequence_editor.active_strip"
    _property_type = (bpy.types.Sequence,)
    bl_category = "Strip"


class SEQUENCER_PT_marker_options(Panel):
    bl_label = "Marker Options"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_category = 'View'

    def draw(self, context):
        layout = self.layout

        tool_settings = context.tool_settings
        st = context.space_data

        layout.prop(tool_settings, "lock_markers")
        layout.prop(st, "use_marker_sync")

class SEQUENCER_PT_view_options(bpy.types.Panel):
    bl_label = "View Options"
    bl_category = "View"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'

    def draw(self, context):
        layout = self.layout

        st = context.space_data
        is_preview = st.view_type in {'PREVIEW', 'SEQUENCER_PREVIEW'}
        is_sequencer_view = st.view_type in {'SEQUENCER', 'SEQUENCER_PREVIEW'}

        if is_sequencer_view:
            layout.prop(st, "show_seconds")
            layout.prop(st, "show_frame_indicator")
            layout.prop(st, "show_strip_offset")
            layout.prop(st, "show_marker_lines")
            layout.menu("SEQUENCER_MT_view_cache")
            layout.prop(st, "show_seconds")

            layout.use_property_split = True
            layout.prop(st, "waveform_display_type")

        if is_preview:
            layout.use_property_split = False
            if st.display_mode == 'IMAGE':
                layout.prop(st, "show_safe_areas")
                layout.prop(st, "show_metadata")
            elif st.display_mode == 'WAVEFORM':
                layout.prop(st, "show_separate_color")


classes = (
    ALL_MT_editormenu,
    SEQUENCER_MT_change,
    SEQUENCER_HT_header,
    SEQUENCER_MT_editor_menus,
    SEQUENCER_MT_view,
    SEQUENCER_MT_view_cache,
    SEQUENCER_MT_view_toggle,
    SEQUENCER_MT_select_inverse,
    SEQUENCER_MT_select_none,
    SEQUENCER_MT_select,
    SEQUENCER_MT_marker,
    SEQUENCER_MT_frame,
    SEQUENCER_MT_add,
    SEQUENCER_MT_add_effect,
    SEQUENCER_MT_add_transitions,
    SEQUENCER_MT_add_empty,
    SEQUENCER_MT_strip,
    SEQUENCER_MT_strip_transform,
    SEQUENCER_MT_strip_input,
    SEQUENCER_MT_strip_lock_mute,
    SEQUENCER_PT_edit,
    SEQUENCER_PT_effect,
    SEQUENCER_PT_input,
    SEQUENCER_PT_sound,
    SEQUENCER_PT_scene,
    SEQUENCER_PT_mask,
    SEQUENCER_PT_filter,
    SEQUENCER_PT_cache_settings,
    SEQUENCER_PT_proxy_settings,
    SEQUENCER_PT_strip_proxy,
    SEQUENCER_PT_strip_cache,
    SEQUENCER_PT_preview,
    SEQUENCER_PT_view,
    SEQUENCER_PT_view_safe_areas,
    SEQUENCER_PT_modifiers,
    SEQUENCER_PT_grease_pencil,
    SEQUENCER_PT_grease_pencil_tools,
    SEQUENCER_PT_custom_props,
    SEQUENCER_PT_marker_options,
    SEQUENCER_PT_view_options
)

if __name__ == "__main__":  # only for live edit.
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)
