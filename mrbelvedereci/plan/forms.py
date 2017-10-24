from github3 import login

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field
from crispy_forms.layout import Fieldset
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.conf import settings

from mrbelvedereci.repository.models import Branch
from mrbelvedereci.build.models import Build


class RunPlanForm(forms.Form):
    branch = forms.ChoiceField(choices=(), label='Branch')
    commit = forms.CharField(required=False)
    keep_org = forms.BooleanField(required=False)

    def __init__(self, plan, repo, user, *args, **kwargs):
        self.plan = plan
        self.repo = repo
        self.user = user
        super(RunPlanForm, self).__init__(*args, **kwargs)
        self.fields['branch'].choices = self._get_branch_choices()
        self.helper = FormHelper()
        self.helper.form_class = 'form-vertical'
        self.helper.form_id = 'run-build-form'
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Choose the branch you want to build',
                Field('branch', css_class='slds-input'),
                css_class='slds-form-element',
            ),
            Fieldset(
                'Enter the commit you want to build.  The HEAD commit on the branch will be used if you do not specify a commit',
                Field('commit', css_class='slds-input'),
                css_class='slds-form-element',
            ),
            Fieldset(
                'Keep org? (scratch orgs only)',
                Field('keep_org', css_class='slds-checkbox'),
                css_class='slds-form-element',
            ),
            FormActions(
                Submit('submit', 'Submit',
                       css_class='slds-button slds-button--brand')
            ),
        )

    def _get_branch_choices(self):
        choices = []
        gh_repo = self.repo.github_api
        for branch in gh_repo.iter_branches():
            choices.append((branch.name, branch.name))
        return tuple(choices)

    def create_build(self):
        commit = self.cleaned_data.get('commit')
        if not commit:
            gh_repo = self.repo.github_api
            gh_branch = gh_repo.branch(self.cleaned_data['branch'])
            commit = gh_branch.commit.sha

        branch, created = Branch.objects.get_or_create(
            repo=self.repo,
            name=self.cleaned_data['branch'],
        )
            
        keep_org = self.cleaned_data.get('keep_org')

        build = Build(
            repo=self.repo,
            plan=self.plan,
            branch=branch,
            commit=commit,
            keep_org=keep_org,
            build_type='manual',
            user=self.user
        )
        build.save()
        
        return build
