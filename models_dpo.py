from tortoise import fields, models
from tortoise.models import Model

class File(Model): # Файл
    file_id = fields.IntField(pk=True)
    file_name = fields.CharField(max_length=255, null=False)
    file_url = fields.CharField(max_length=255, null=False) 

    class Meta:
        table = "files"
        schema = "dpo"
        
        
class EducationLevel(models.Model): # Тип образования
    level_id = fields.IntField(pk=True)
    level_name = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "education_levels"
        schema = "dpo"
        
        
class RegistrationForm(models.Model): # Регистрационная анкета
    form_id = fields.IntField(pk=True)
    last_name = fields.CharField(max_length=255, null=False)
    first_name = fields.CharField(max_length=255, null=False)
    middle_name = fields.CharField(max_length=255, null=False)
    email = fields.CharField(max_length=255, null=False)
    birth_date = fields.DateField(null=False)
    snils = fields.CharField(max_length=255, null=False)
    passport_data = fields.CharField(max_length=255, null=False)
    passport_issued_by = fields.CharField(max_length=255, null=False)
    passport_issue_date = fields.DateField(null=False)
    
    passport_copy_main_page = fields.ForeignKeyField('models.File', 
                                                     null=False, 
                                                     on_delete=fields.CASCADE)
    
    passport_copy_registration_page = fields.ForeignKeyField('models.File', 
                                                             related_name='registration_forms_pass_reg', 
                                                             null=False, 
                                                             on_delete=fields.CASCADE)
    
    registration_address = fields.CharField(max_length=255, null=False)
    index = fields.CharField(max_length=10, null=False)
    actual_address = fields.CharField(max_length=255, null=False)
    actual_index = fields.CharField(max_length=10, null=False)
    mobile_phone = fields.CharField(max_length=20, null=False)
    
    education_level = fields.ForeignKeyField('models.EducationLevel', 
                                             related_name='registration_forms', 
                                             null=False, 
                                             on_delete=fields.CASCADE)
    
    diploma_name = fields.CharField(max_length=255, null=False)
    diploma_series = fields.CharField(max_length=20, null=False)
    diploma_number = fields.CharField(max_length=20, null=False)
    diploma_issue_date = fields.DateField(null=False)
    
    diploma_copy = fields.ForeignKeyField('models.File', 
                                          related_name='diploma_forms', 
                                          null=False, 
                                          on_delete=fields.CASCADE)
    assessment_sheet_copy = fields.ForeignKeyField('models.File', 
                                                   related_name='registration_forms_assessment', 
                                                   null=True, 
                                                   on_delete=fields.SET_NULL)
    
    name_change_document_copy = fields.ForeignKeyField('models.File', 
                                                       related_name='registration_forms_name_change', 
                                                       null=True, 
                                                       on_delete=fields.SET_NULL) 
    application = fields.ForeignKeyField('models.File', 
                                         related_name='registration_forms_application', 
                                         null=False, 
                                         on_delete=fields.CASCADE)

    class Meta:
        table = "registration_forms"
        schema = "dpo"
        
        
class Acquiring(models.Model): # Эквайринг
    acquiring_id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=False)
    
    class Meta:
        table = "acquirings"
        schema = "dpo"
        
        
class Client(Model): # Клиент
    id = fields.IntField(pk=True) 
    last_name = fields.CharField(max_length=255, null=False) 
    first_name = fields.CharField(max_length=255, null=False) 
    middle_name = fields.CharField(max_length=255, null=False)
    birth_date = fields.DateField(null=False)
    email = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "clients" 
        schema = "dpo"
        
        
class InPersonReceipt(models.Model): # Очное получение ведомости клиентом
    client = fields.ForeignKeyField(
        "models.Client", 
        related_name="in_person_receipts",
        null=False,
        on_delete=fields.CASCADE
    )
    tracking_number = fields.CharField(
        max_length=255,
        null=True
    )
    signed_document = fields.ForeignKeyField(
        "models.File",
        related_name="in_person_receipts",
        null=True,
        on_delete=fields.SET_NULL
    )

    class Meta:
        table = "in_person_receipts"
        schema = "dpo"
        
        
class FinancialTransaction(models.Model): # Финансовые транзакции клиента
    transaction_id = fields.IntField(pk=True)
    amount = fields.DecimalField(max_digits=10, decimal_places=2)
    transaction_date = fields.DateField()
    fls = fields.DecimalField(max_digits=10, decimal_places=2)
    nds = fields.DecimalField(max_digits=10, decimal_places=2)
    amount_on_fls = fields.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        table = "financial_transactions"
        schema = "dpo"
        

class ClientFinance(models.Model): # Финансы клиента
    client = fields.ForeignKeyField(
        'models.Client',
        related_name='finances',
        on_delete=fields.CASCADE,
        null=False
    )
    amount = fields.DecimalField(max_digits=10, decimal_places=2, null=True)
    date = fields.DateField(null=True)
    
    act = fields.ForeignKeyField(
        "models.File",
        related_name="finances",
        null=True,
        on_delete=fields.SET_NULL
    )

    class Meta:
        table = "client_finances"
        schema = "dpo"
        
        
class EducationalProgramStatus(models.Model): # Статус образовательной программы клиента
    status_id = fields.IntField(pk=True)
    status_name = fields.CharField(max_length=255)

    class Meta:
        table = "educational_program_status"
        schema = "dpo"

        
class ClientType(Model): # Тип клиента
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "client_types" 
        schema = "dpo"
        
class EducationalProgramType(Model): # Тип образовательной программы
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=True) 

    class Meta:
        table = "educational_program_types"
        schema = "dpo"
        
        
class DocumentType(Model): # Тип документа, выдаваемового после прохождения обучения
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "document_types"
        schema = "dpo"


class LearningForm(Model): # Форма обучения
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "learning_forms"
        schema = "dpo"
        

class EducationalProgram(Model): # Образовательная программа
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=False)
    
    learning_form = fields.ForeignKeyField(
        'models.LearningForm', 
        related_name='educational_programs', 
        null=False,
        on_delete=fields.CASCADE
    )
    
    program_type = fields.ForeignKeyField(
        'models.EducationalProgramType', 
        related_name='educational_programs', 
        null=False,
        on_delete=fields.CASCADE
    )
    
    landing = fields.ForeignKeyField(
        'models.File', 
        related_name='educational_program_landing', 
        null=True, 
        on_delete=fields.SET_NULL
    )
    
    presentation = fields.ForeignKeyField(
        'models.File', 
        related_name='educational_program_presentation', 
        null=True, 
        on_delete=fields.SET_NULL
    )
    
    date = fields.DateField(null=True) 
    
    document_type = fields.ForeignKeyField(
        'models.DocumentType', 
        related_name='educational_programs', 
        null=True,
        on_delete=fields.SET_NULL
    )
    
    quantity = fields.IntField(null=True)
    description = fields.CharField(max_length=255, null=True)
    fgos = fields.CharField(max_length=255, null=True)
    organizers = fields.CharField(max_length=255, null=True)
    price = fields.FloatField(null=True)
    
    end_date = fields.DateField(null=True)
    start_date = fields.DateField(null=True)

    class Meta:
        table = "educational_programs"
        schema = "dpo"
        
        
class ProgramStream(Model): # Поток образовательной программы
    id = fields.CharField(max_length=255, pk=True)

    educational_program = fields.ForeignKeyField(
        'models.EducationalProgram',
        related_name='program_streams',
        null=False
    )

    number = fields.CharField(max_length=50, null=True)
    date = fields.DateField(null=True)

    class Meta:
        table = "program_stream"
        schema = "dpo"
        
        
class ClientEducationalProgram(models.Model): # Образовательные программы клиента
    id = fields.IntField(pk=True) 
    client = fields.ForeignKeyField(
        'models.Client',
        related_name='educational_programs',
        on_delete=fields.CASCADE,
        null=False
    )
    program_stream = fields.ForeignKeyField(
        'models.ProgramStream',
        related_name='educational_programs',
        on_delete=fields.CASCADE,
        null=False
    )
    contract = fields.ForeignKeyField(
        'models.File',
        related_name='educational_program_contracts',
        on_delete=fields.SET_NULL,
        null=True
    )
    postpayment = fields.BooleanField(default=False, null=False)
    registration_form = fields.ForeignKeyField(
        'models.RegistrationForm',
        related_name='educational_programs',
        on_delete=fields.SET_NULL,
        null=True
    )
    client_type = fields.ForeignKeyField(
        'models.ClientType', 
        related_name='educational_programs',
        on_delete=fields.CASCADE,
        null=False 
    )
    status = fields.ForeignKeyField(
        'models.EducationalProgramStatus', 
        related_name='educational_programs',
        on_delete=fields.CASCADE,
        null=False 
    )
    comment = fields.CharField(max_length=255, null=True)  
    
    enrollment_order = fields.ForeignKeyField(
        'models.File',
        related_name='educational_program_enrollment_orders',
        on_delete=fields.SET_NULL,
        null=True
    )
    date_of_enrollment_order = fields.DateField(null=True)
    
    expulsion_order = fields.ForeignKeyField(
        'models.File',
        related_name='educational_program_expulsion_orders',
        on_delete=fields.SET_NULL,
        null=True
    )
    date_of_expulsion_order = fields.DateField(null=True)

    class Meta:
        table = "client_educational_programs"
        schema = "dpo"
        

class ClientEducationalProgramInterimOrder(Model): # Приказы о промежуточной аттестации образовательной программы клиента
    client_educational_program = fields.ForeignKeyField(
        'models.EducationalProgram',
        related_name='interim_orders',
        on_delete=fields.CASCADE,
        null=False
    )
    order = fields.ForeignKeyField(
        'models.File', 
        related_name='interim_orders',
        on_delete=fields.SET_NULL,
        null=True
    )
    date = fields.DateField(null=True)

    class Meta:
        table = "client_educational_program_interim_orders"
        schema = "dpo"


class ClientParent(Model): # Родители клиента
    client = fields.ForeignKeyField(
        'models.Client',
        related_name='parents',
        on_delete=fields.CASCADE,
        null=False
    )
    parent_name = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "client_parents"
        schema = "dpo"


class EducationalProgramModule(Model): # Модуль образовательной программы
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255, null=False)
    academic_hours = fields.IntField(null=False)

    educational_program = fields.ForeignKeyField(
        'models.EducationalProgram',
        related_name='modules',
        null=False,
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "educational_program_modules"
        schema = "dpo"
        

class ClientGrade(Model): # Оценки клиента
    program_module = fields.ForeignKeyField(
        'models.EducationalProgramModule',
        related_name='client_grades',
        on_delete=fields.CASCADE,
        null=False) 
    client = fields.ForeignKeyField(
        'models.Client',
        related_name='client_grades',
        on_delete=fields.CASCADE,
        null=False) 
    grade = fields.IntField(null=True)
    quantity = fields.IntField(null=True)

    class Meta:
        table = "client_grades"
        schema = "dpo"
        

class ProgramStreamTeacher(Model): # Преподаватель потока образовательной программы
    program_stream = fields.ForeignKeyField(
        'models.ProgramStream', 
        related_name='teachers', 
        on_delete=fields.CASCADE,
        null=False) 
    name = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "program_stream_teachers"
        schema = "dpo"
        
        
class ProgramStreamManager(Model): # Менеджер образовательной программы
    educational_program = fields.ForeignKeyField(
        'models.EducationalProgram', 
        related_name='managers', 
        on_delete=fields.CASCADE,
        null=False) 
    name = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "program_stream_managers"
        schema = "dpo"
        

class ProgramStreamCurator(Model): # Куратор потока образовательной программы
    program_stream = fields.ForeignKeyField(
        'models.ProgramStream', 
        related_name='curators', 
        on_delete=fields.CASCADE,
        null=False) 
    name = fields.CharField(max_length=255, null=False)

    class Meta:
        table = "program_stream_curators"
        schema = "dpo"
        
     
class Annotation(Model): # Аннотация образовательной программы
    educational_program = fields.ForeignKeyField(
        'models.EducationalProgram',
        related_name='annotations',
        null=False
    )
    approval_date = fields.DateField(null=False)
    document = fields.ForeignKeyField(
        'models.File', 
        related_name='annotations', 
        null=False, 
        on_delete=fields.CASCADE)

    class Meta:
        table = "annotations" 
        schema = "dpo"


class ApprovedProgram(Model): # Одобренные программы
    program_stream = fields.ForeignKeyField(
        'models.ProgramStream',
        related_name='approved_programs',
        null=False
    )
    approval_date = fields.DateField(null=False)
    document = fields.ForeignKeyField(
        'models.File', 
        related_name='approved_programs', 
        null=False, 
        on_delete=fields.CASCADE
    )

    class Meta:
        table = "approved_programs" 
        schema = "dpo" 
        

class ClassSchedule(Model): # Время занятий потока образовательной программы
    id = fields.IntField(pk=True)
    
    program_stream = fields.ForeignKeyField(
        'models.ProgramStream',
        related_name='class_schedules',
        null=False,
        on_delete=fields.CASCADE
    )
    
    day_of_week = fields.IntField(null=False)
    start_time = fields.TimeField(null=False)
    end_time = fields.TimeField(null=False)

    class Meta:
        table = "class_schedules"
        schema = "dpo"