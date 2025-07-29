##############################################################################
#
# Copyright (c) 2012 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: btn.py 5172 2025-03-12 23:32:53Z felipe.souza $
"""
from __future__ import absolute_import
__docformat__ = "reStructuredText"
from zope.interface import implementer

import zope.interface

import z3c.form.button

import j01.jsonrpc.btn
import j01.dialog.btn

from j01.wizard import interfaces
from j01.wizard.interfaces import _


class WizardButtonActions(z3c.form.button.ButtonActions):
    """Wizard Button Actions."""

    @property
    def backActions(self):
        return [action for action in list(self.values())
                if interfaces.IBackButton.providedBy(action.field)]

    @property
    def nextActions(self):
        return [action for action in list(self.values())
                if interfaces.INextButton.providedBy(action.field)]


# jsonrpc
@implementer(interfaces.INextButton)
class JSONRPCNextButton(j01.jsonrpc.btn.JSONRPCButton):
    """JSONRPC next button"""



@implementer(interfaces.IBackButton)
class JSONRPCBackButton(j01.jsonrpc.btn.JSONRPCButton):
    """JSONRPC back button"""



# dialog
@implementer(interfaces.INextButton)
class DialogNextButton(j01.dialog.btn.DialogButton):
    """Dialog next button"""



@implementer(interfaces.IBackButton)
class DialogBackButton(j01.dialog.btn.DialogButton):
    """Dialog back button"""



# jsonrpc wizard buttons
class IJSONRPCWizardButtons(zope.interface.Interface):
    """JSONRPC wizard button interfaces."""

    back = JSONRPCBackButton(
        title=_('Back'),
        condition=lambda form: form.showBackButton)

    next = JSONRPCNextButton(
        title=_('Next'),
        condition=lambda form: form.showNextButton)

    complete = JSONRPCNextButton(
        title=_('Complete'),
        condition=lambda form: form.showCompleteButton)


# dialog wizard buttons
class IDialogWizardButtons(zope.interface.Interface):
    """Dialog wizard button interfaces."""

    back = DialogBackButton(
        title=_('Back'),
        condition=lambda form: form.showBackButton)

    next = DialogNextButton(
        title=_('Next'),
        condition=lambda form: form.showNextButton)

    complete = DialogNextButton(
        title=_('Complete'),
        condition=lambda form: form.showCompleteButton)
