from django.db import models
from django.forms import ModelForm, TextInput, Textarea, SelectMultiple, CheckboxSelectMultiple
from django.contrib.auth.models import User

# --- Competency System Hierarchy ---

# Description of common attributes:
#  public: whether a non-logged in user can see this element
#  description: a public-facing narrative description of this element
#  student-friendly: Many parts of a standards system are written in 'teacher language',
#    which is not very accessible to students. This is a rephrasing of the element in
#    language that is easier for students to understand.

class School(models.Model):
    name = models.CharField(max_length=500)

    def __unicode__(self):
        return self.name

class SubjectArea(models.Model):
    subject_area = models.CharField(max_length=500)
    school = models.ForeignKey(School)
    public = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.subject_area

    class Meta:
        order_with_respect_to = 'school'

    def is_parent_public(self):
        return True

    def get_parent(self):
        return self.school

class SubdisciplineArea(models.Model):
    subdiscipline_area = models.CharField(max_length=500)
    subject_area = models.ForeignKey(SubjectArea)
    public = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.subdiscipline_area

    class Meta:
        order_with_respect_to = 'subject_area'

    def is_parent_public(self):
        return self.subject_area.public

    def get_parent(self):
        return self.subject_area

class CompetencyArea(models.Model):
    competency_area = models.CharField(max_length=500)
    subject_area = models.ForeignKey(SubjectArea)
    subdiscipline_area = models.ForeignKey(SubdisciplineArea, blank=True, null=True)
    public = models.BooleanField(default=False)
    student_friendly = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.competency_area

    class Meta:
        order_with_respect_to = 'subject_area'

    def is_parent_public(self):
        # If no sda, then only use subject_area
        if self.subdiscipline_area:
            sda_public = self.subdiscipline_area.public
        else:
            sda_public = True

        if self.subject_area.public and sda_public:
            return True
        else:
            return False

    def get_parent(self):
        return self.subject_area

class Level(models.Model):
    APPRENTICE = 'Apprentice'
    TECHNICIAN = 'Technician'
    MASTER = 'Master'
    PROFESSIONAL = 'Professional'
    LEVEL_TYPE_CHOICES = ( (APPRENTICE, 'Apprentice'), (TECHNICIAN, 'Technician'),
                           (MASTER, 'Master'), (PROFESSIONAL, 'Professional') )
    level_type = models.CharField(max_length=500, choices=LEVEL_TYPE_CHOICES)
    level_description = models.CharField(max_length=5000)
    competency_area = models.ForeignKey(CompetencyArea)
    public = models.BooleanField(default=False)

    def __unicode__(self):
        return self.level_description

    class Meta:
        unique_together = ('competency_area', 'level_type',)
        order_with_respect_to = 'competency_area'

    def is_parent_public(self):
        return self.competency_area.public

    def get_parent(self):
        return self.competency_area

class EssentialUnderstanding(models.Model):
    essential_understanding = models.CharField(max_length=2000)
    competency_area = models.ForeignKey(CompetencyArea)
    public = models.BooleanField(default=False)
    student_friendly = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.essential_understanding

    class Meta:
        order_with_respect_to = 'competency_area'

    def is_parent_public(self):
        return self.competency_area.public

    def get_parent(self):
        return self.competency_area

class LearningTarget(models.Model):
    learning_target = models.CharField(max_length=2000)
    essential_understanding = models.ForeignKey(EssentialUnderstanding)
    public = models.BooleanField(default=False)
    student_friendly = models.TextField(blank=True)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.learning_target

    class Meta:
        order_with_respect_to = 'essential_understanding'

    def is_parent_public(self):
        return self.essential_understanding.public

    def get_parent(self):
        return self.essential_understanding


# --- Pathways ---
from django.db.models import Q
class Pathway(models.Model):
    name = models.CharField(max_length=500)
    school = models.ForeignKey(School)
    subject_areas = models.ManyToManyField(SubjectArea)
    subdiscipline_areas = models.ManyToManyField(SubdisciplineArea, blank=True, null=True)
    competency_areas = models.ManyToManyField(CompetencyArea, blank=True, null=True)
    essential_understandings = models.ManyToManyField(EssentialUnderstanding, blank=True, null=True)
    learning_targets = models.ManyToManyField(LearningTarget, blank=True, null=True)
    public = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name


# --- User Information ---

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    # User is allowed to edit any aspect of any school in this list.
    schools = models.ManyToManyField(School, blank=True, null=True)
    # User is allowed to edit any descendent of any subject_area in this list.
    subject_areas = models.ManyToManyField(SubjectArea, blank=True, null=True)
    # User is allowed to edit any pathway in this list.
    pathways = models.ManyToManyField(Pathway, blank=True, null=True)


# --- ModelForms ---
class SubjectAreaForm(ModelForm):
    class Meta:
        model = SubjectArea
        fields = ('subject_area', 'description')
        widgets = {
            'subject_area': TextInput(attrs={'class': 'span4'}),
            'description': Textarea(attrs={'rows': 5, 'class': 'span8'}),
            }

class SubdisciplineAreaForm(ModelForm):
    class Meta:
        model = SubdisciplineArea
        fields = ('subdiscipline_area', 'description')
        widgets = {
            'subdiscipline_area': TextInput(attrs={'class': 'span4'}),
            'description': Textarea(attrs={'rows': 5, 'class': 'span8'}),
            }

class CompetencyAreaForm(ModelForm):
    class Meta:
        model = CompetencyArea
        fields = ('competency_area', 'student_friendly', 'description')
        # Bootstrap controls width of Textarea, ignoring the 'cols' setting. Can also use 'class': 'input-block-level'
        widgets = {'competency_area': Textarea(attrs={'rows': 5, 'class': 'span8'}),
                   'student_friendly': Textarea(attrs={'rows': 5, 'class': 'span8'}),
                   'description': Textarea(attrs={'rows': 5, 'class': 'span8'}),
                   }

class EssentialUnderstandingForm(ModelForm):
    class Meta:
        model = EssentialUnderstanding
        fields = ('essential_understanding', 'student_friendly', 'description')
        # Bootstrap controls width of Textarea, ignoring the 'cols' setting. Can also use 'class': 'input-block-level'
        widgets = {'essential_understanding': Textarea(attrs={'rows': 5, 'class': 'span8'}),
                   'student_friendly': Textarea(attrs={'rows': 5, 'class': 'span8'}),
                   'description': Textarea(attrs={'rows': 5, 'class': 'span8'}),
                   }

class LevelForm(ModelForm):
    class Meta:
        model = Level
        fields = ('level_type', 'level_description',)
        # Bootstrap controls width of Textarea, ignoring the 'cols' setting. Can also use 'class': 'input-block-level'
        widgets = {'level_description': Textarea(attrs={'rows': 5, 'class': 'span8'}) }

class LearningTargetForm(ModelForm):
    class Meta:
        model = LearningTarget
        fields = ('learning_target', 'student_friendly', 'description')
        # Bootstrap controls width of Textarea, ignoring the 'cols' setting. Can also use 'class': 'input-block-level'
        widgets = {'learning_target': Textarea(attrs={'rows': 5, 'class': 'span8'}),
                   'student_friendly': Textarea(attrs={'rows': 5, 'class': 'span8'}),
                   'description': Textarea(attrs={'rows': 5, 'class': 'span8'}),
                   }

class PathwayForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PathwayForm, self).__init__(*args, **kwargs)
        pathway = self.instance

        # sas
        self.fields['subject_areas'].queryset = pathway.school.subjectarea_set.all()

        # sdas
        if pathway.subject_areas.all():
            sda_queryset = SubdisciplineArea.objects.none()
            for sa in pathway.subject_areas.all():
                sda_queryset = sda_queryset | sa.subdisciplinearea_set.all()
            self.fields['subdiscipline_areas'].queryset = sda_queryset

        # cas
        if pathway.subject_areas.all():
            ca_queryset = CompetencyArea.objects.none()
            # General subject area competencies:
            for sa in pathway.subject_areas.all():
                ca_queryset = ca_queryset | sa.competencyarea_set.all().filter(subdiscipline_area=None)
            # Subdiscipline area competencies:
            if pathway.subdiscipline_areas.all():
                for sda in pathway.subdiscipline_areas.all():
                    ca_queryset = ca_queryset | sda.competencyarea_set.all()
            self.fields['competency_areas'].queryset = ca_queryset

        # eus
        if pathway.competency_areas.all():
            eu_queryset = EssentialUnderstanding.objects.none()
            for ca in pathway.competency_areas.all():
                eu_queryset |= ca.essentialunderstanding_set.all()
            self.fields['essential_understandings'].queryset = eu_queryset

        # lts
        if pathway.essential_understandings.all():
            lt_queryset = LearningTarget.objects.none()
            for eu in pathway.essential_understandings.all():
                lt_queryset |= eu.learningtarget_set.all()
            self.fields['learning_targets'].queryset = lt_queryset

    class Meta:
        model = Pathway
        # Bootstrap controls width of Textarea, ignoring the 'cols' setting. Can also use 'class': 'input-block-level'
        #  Consider CheckboxSelectMultiple for some of these, especially eus and lts
        # number of items to show in longer dropdown lists:
        widgets = {
            'name': TextInput(attrs={'class': 'span4'}),
            'subject_areas': SelectMultiple(attrs={'class': 'span4', 'size': 5}),
            'subdiscipline_areas': SelectMultiple(attrs={'class': 'span4', 'size': 5}),
            'competency_areas': SelectMultiple(attrs={'class': 'span4', 'size': 15}),
            'essential_understandings': SelectMultiple(attrs={'class': 'span8', 'size': 20}),
            'learning_targets': SelectMultiple(attrs={'class': 'span8', 'size': 20}),
            }
