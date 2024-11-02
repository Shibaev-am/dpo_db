from tortoise import fields
from models.base import BaseModel


class File(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    name = fields.CharField(max_length=255, null=True, description="Имя")
    url = fields.CharField(max_length=4096, null=True, description="Ссылка")

    class Meta:
        description = "Файл"


class EducationLevel(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    name = fields.CharField(max_length=255, null=True, description="Название")

    class Meta:
        description = "Тип образования"


class RegistrationForm(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    last_name = fields.CharField(max_length=255, null=True, description="Фамилия")
    first_name = fields.CharField(max_length=255, null=True, description="Имя")
    middle_name = fields.CharField(max_length=255, null=True, description="Отчество")
    email = fields.CharField(
        max_length=255, null=True, description="Электронная почта"
    )
    birth_date = fields.DateField(null=True, description="Дата рождения")
    snils = fields.CharField(max_length=255, null=True, description="СНИЛС")
    passport_data = fields.CharField(
        max_length=255, null=True, description="Данные паспорта"
    )
    passport_issued_by = fields.CharField(
        max_length=255, null=True, description="Кем выдан паспорт"
    )
    passport_issue_date = fields.DateField(
        null=True, description="Дата выдачи паспорта"
    )

    passport_copy_main_page = fields.ForeignKeyField(
        "models.File",
        null=True,
        on_delete=fields.CASCADE,
        description="Копия главной страницы паспорта",
    )

    passport_copy_registration_page = fields.ForeignKeyField(
        "models.File",
        related_name="registration_forms_pass_reg",
        null=True,
        on_delete=fields.CASCADE,
        description="Копия страницы регистрации паспорта",
    )

    registration_address = fields.CharField(
        max_length=255, null=True, description="Адрес регистрации"
    )
    index = fields.CharField(max_length=10, null=True, description="Индекс")
    actual_address = fields.CharField(
        max_length=255, null=True, description="Фактический адрес"
    )
    actual_index = fields.CharField(
        max_length=10, null=True, description="Фактический индекс"
    )
    mobile_phone = fields.CharField(
        max_length=20, null=True, description="Мобильный телефон"
    )

    education_level = fields.ForeignKeyField(
        "models.EducationLevel",
        related_name="registration_forms",
        null=True,
        on_delete=fields.CASCADE,
        description="Уровень образования",
    )

    diploma_name = fields.CharField(
        max_length=255, null=True, description="Название диплома"
    )
    diploma_series = fields.CharField(
        max_length=20, null=True, description="Серия диплома"
    )
    diploma_number = fields.CharField(
        max_length=20, null=True, description="Номер диплома"
    )
    diploma_issue_date = fields.DateField(null=True, description="Дата выдачи диплома")

    diploma_copy = fields.ForeignKeyField(
        "models.File",
        related_name="diploma_forms",
        null=True,
        on_delete=fields.CASCADE,
        description="Копия диплома",
    )
    assessment_sheet_copy = fields.ForeignKeyField(
        "models.File",
        related_name="registration_forms_assessment",
        null=True,
        on_delete=fields.SET_NULL,
        description="Копия оценочного листа",
    )

    name_change_document_copy = fields.ForeignKeyField(
        "models.File",
        related_name="registration_forms_name_change",
        null=True,
        on_delete=fields.SET_NULL,
        description="Копия документа о смене имени",
    )
    application = fields.ForeignKeyField(
        "models.File",
        related_name="registration_forms_application",
        null=True,
        on_delete=fields.CASCADE,
        description="Заявление",
    )

    class Meta:
        description = "Регистрационная анкета"


class Acquiring(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    name = fields.CharField(max_length=255, null=True, description="Название")

    class Meta:
        description = "Эквайринг"


class Client(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    last_name = fields.CharField(max_length=255, null=True, description="Фамилия")
    first_name = fields.CharField(max_length=255, null=True, description="Имя")
    middle_name = fields.CharField(max_length=255, null=True, description="Отчество")
    birth_date = fields.DateField(null=True, description="Дата рождения")
    email = fields.CharField(
        max_length=255, null=True, description="Электронная почта"
    )

    class Meta:
        description = "Клиент"


class InPersonReceipt(BaseModel):
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="in_person_receipts",
        null=True,
        on_delete=fields.CASCADE,
        description="Клиент",
    )
    tracking_number = fields.CharField(
        max_length=255, null=True, description="Номер отслеживания"
    )
    signed_document = fields.ForeignKeyField(
        "models.File",
        related_name="in_person_receipts",
        null=True,
        on_delete=fields.SET_NULL,
        description="Подписанный документ",
    )

    class Meta:
        description = "Очное получение ведомости клиентом"


class FinancialTransaction(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    amount = fields.DecimalField(max_digits=10, decimal_places=2, description="Сумма")
    transaction_date = fields.DateField(description="Дата транзакции")
    fls = fields.DecimalField(max_digits=10, decimal_places=2, description="ФЛС")
    nds = fields.DecimalField(max_digits=10, decimal_places=2, description="НДС")
    amount_on_fls = fields.DecimalField(
        max_digits=10, decimal_places=2, description="Сумма на ФЛС"
    )

    class Meta:
        description = "Финансовые транзакции клиента"


class ClientFinance(BaseModel):
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="finances",
        on_delete=fields.CASCADE,
        null=True,
        description="Клиент",
    )
    amount = fields.DecimalField(
        max_digits=10, decimal_places=2, null=True, description="Сумма"
    )
    date = fields.DateField(null=True, description="Дата")

    act = fields.ForeignKeyField(
        "models.File",
        related_name="finances",
        null=True,
        on_delete=fields.SET_NULL,
        description="Акт",
    )

    class Meta:
        description = "Финансы клиента"


class EducationalProgramStatus(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    status_name = fields.CharField(
        max_length=255, null=True, description="Название статуса"
    )

    class Meta:
        description = "Статус образовательной программы клиента"


class ClientType(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    name = fields.CharField(max_length=255, null=True, description="Название")

    class Meta:
        description = "Тип клиента"


class EducationalProgramType(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    name = fields.CharField(max_length=255, null=True, description="Название")

    class Meta:
        description = "Тип образовательной программы"


class DocumentType(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    name = fields.CharField(max_length=255, null=True, description="Название")

    class Meta:
        description = "Тип документа, выдаваемового после прохождения обучения"


class LearningForm(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    name = fields.CharField(max_length=255, null=True, description="Название")

    class Meta:
        description = "Форма обучения"


class EducationalProgram(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    name = fields.CharField(max_length=255, null=True, description="Название")

    learning_form = fields.ForeignKeyField(
        "models.LearningForm",
        related_name="educational_programs",
        null=True,
        on_delete=fields.CASCADE,
        description="Форма обучения",
    )

    program_type = fields.ForeignKeyField(
        "models.EducationalProgramType",
        related_name="educational_programs",
        null=True,
        on_delete=fields.CASCADE,
        description="Тип образовательной программы",
    )

    landing = fields.ForeignKeyField(
        "models.File",
        related_name="educational_program_landing",
        null=True,
        on_delete=fields.SET_NULL,
        description="Лендинг",
    )

    presentation = fields.ForeignKeyField(
        "models.File",
        related_name="educational_program_presentation",
        null=True,
        on_delete=fields.SET_NULL,
        description="Презентация",
    )

    date = fields.DateField(null=True, description="Дата")

    document_type = fields.ForeignKeyField(
        "models.DocumentType",
        related_name="educational_programs",
        null=True,
        on_delete=fields.SET_NULL,
        description="Тип документа",
    )

    quantity = fields.IntField(null=True, description="Количество")
    description = fields.CharField(max_length=255, null=True, description="Описание")
    fgos = fields.CharField(max_length=255, null=True, description="ФГОС")
    organizers = fields.CharField(max_length=255, null=True, description="Организаторы")
    price = fields.DecimalField(
        max_digits=10, decimal_places=2, null=True, description="Цена"
    )

    end_date = fields.DateField(null=True, description="Дата окончания")
    start_date = fields.DateField(null=True, description="Дата начала")

    class Meta:
        description = "Образовательная программа"


class ProgramStream(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")

    educational_program = fields.ForeignKeyField(
        "models.EducationalProgram",
        related_name="program_streams",
        null=True,
        on_delete=fields.CASCADE,
        description="Образовательная программа",
    )

    number = fields.CharField(max_length=50, null=True, description="Номер")
    date = fields.DateField(null=True, description="Дата")

    class Meta:
        description = "Поток образовательной программы"


class ClientEducationalProgram(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="educational_programs",
        on_delete=fields.CASCADE,
        null=True,
        description="Клиент",
    )
    program_stream = fields.ForeignKeyField(
        "models.ProgramStream",
        related_name="educational_programs",
        on_delete=fields.CASCADE,
        null=True,
        description="Поток образовательной программы",
    )
    contract = fields.ForeignKeyField(
        "models.File",
        related_name="educational_program_contracts",
        on_delete=fields.SET_NULL,
        null=True,
        description="Контракт",
    )
    postpayment = fields.BooleanField(
        default=False, null=True, description="Постоплата"
    )
    registration_form = fields.ForeignKeyField(
        "models.RegistrationForm",
        related_name="educational_programs",
        on_delete=fields.SET_NULL,
        null=True,
        description="Регистрационная форма",
    )
    client_type = fields.ForeignKeyField(
        "models.ClientType",
        related_name="educational_programs",
        on_delete=fields.CASCADE,
        null=True,
        description="Тип клиента",
    )
    status = fields.ForeignKeyField(
        "models.EducationalProgramStatus",
        related_name="educational_programs",
        on_delete=fields.CASCADE,
        null=True,
        description="Статус образовательной программы",
    )
    comment = fields.CharField(max_length=255, null=True, description="Комментарий")

    enrollment_order = fields.ForeignKeyField(
        "models.File",
        related_name="educational_program_enrollment_orders",
        on_delete=fields.SET_NULL,
        null=True,
        description="Приказ о зачислении",
    )
    date_of_enrollment_order = fields.DateField(
        null=True, description="Дата приказа о зачислении"
    )

    expulsion_order = fields.ForeignKeyField(
        "models.File",
        related_name="educational_program_expulsion_orders",
        on_delete=fields.SET_NULL,
        null=True,
        description="Приказ об отчислении",
    )
    date_of_expulsion_order = fields.DateField(
        null=True, description="Дата приказа об отчислении"
    )

    class Meta:
        description = "Образовательные программы клиента"


class ClientEducationalProgramInterimOrder(BaseModel):
    client_educational_program = fields.ForeignKeyField(
        "models.ClientEducationalProgram",
        related_name="interim_orders",
        on_delete=fields.CASCADE,
        null=True,
        description="Образовательная программа клиента",
    )
    order = fields.ForeignKeyField(
        "models.File",
        related_name="interim_orders",
        on_delete=fields.SET_NULL,
        null=True,
        description="Приказ",
    )
    date = fields.DateField(null=True, description="Дата")

    class Meta:
        description = (
            "Приказы о промежуточной аттестации образовательной программы клиента"
        )


class ClientParent(BaseModel):
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="parents",
        on_delete=fields.CASCADE,
        null=True,
        description="Клиент",
    )
    parent_name = fields.CharField(
        max_length=255, null=True, description="Имя родителя"
    )

    class Meta:
        description = "Родители клиента"


class EducationalProgramModule(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")
    name = fields.CharField(max_length=255, null=True, description="Название")
    academic_hours = fields.IntField(null=True, description="Академические часы")

    educational_program = fields.ForeignKeyField(
        "models.EducationalProgram",
        related_name="modules",
        null=True,
        on_delete=fields.CASCADE,
        description="Образовательная программа",
    )

    class Meta:
        description = "Модуль образовательной программы"


class ClientGrade(BaseModel):
    program_module = fields.ForeignKeyField(
        "models.EducationalProgramModule",
        related_name="client_grades",
        on_delete=fields.CASCADE,
        null=True,
        description="Модуль образовательной программы",
    )
    client = fields.ForeignKeyField(
        "models.Client",
        related_name="client_grades",
        on_delete=fields.CASCADE,
        null=True,
        description="Клиент",
    )
    grade = fields.IntField(null=True, description="Оценка")
    quantity = fields.IntField(null=True, description="Количество")

    class Meta:
        description = "Оценки клиента"


class ProgramStreamTeacher(BaseModel):
    program_stream = fields.ForeignKeyField(
        "models.ProgramStream",
        related_name="teachers",
        on_delete=fields.CASCADE,
        null=True,
        description="Поток образовательной программы",
    )
    name = fields.CharField(
        max_length=255,
        null=True,
        description="Имя преподавателя",
    )

    class Meta:
        description = "Преподаватель потока образовательной программы"


class ProgramStreamManager(BaseModel):
    educational_program = fields.ForeignKeyField(
        "models.EducationalProgram",
        related_name="managers",
        on_delete=fields.CASCADE,
        null=True,
        description="Образовательная программа",
    )
    name = fields.CharField(
        max_length=255,
        null=True,
        description="Имя менеджера",
    )

    class Meta:
        description = "Менеджер образовательной программы"


class ProgramStreamCurator(BaseModel):
    program_stream = fields.ForeignKeyField(
        "models.ProgramStream",
        related_name="curators",
        on_delete=fields.CASCADE,
        null=True,
        description="Поток образовательной программы",
    )
    name = fields.CharField(
        max_length=255,
        null=True,
        description="Имя куратора",
    )

    class Meta:
        description = "Куратор потока образовательной программы"


class Annotation(BaseModel):
    educational_program = fields.ForeignKeyField(
        "models.EducationalProgram",
        related_name="annotations",
        null=True,
        on_delete=fields.CASCADE,
        description="Образовательная программа",
    )
    approval_date = fields.DateField(null=True, description="Дата утверждения")
    document = fields.ForeignKeyField(
        "models.File",
        related_name="annotations",
        null=True,
        on_delete=fields.CASCADE,
        description="Документ",
    )

    class Meta:
        description = "Аннотация образовательной программы"


class ApprovedProgram(BaseModel):
    program_stream = fields.ForeignKeyField(
        "models.ProgramStream",
        related_name="approved_programs",
        null=True,
        on_delete=fields.CASCADE,
        description="Поток образовательной программы",
    )
    approval_date = fields.DateField(
        null=True,
        description="Дата утверждения",
    )
    document = fields.ForeignKeyField(
        "models.File",
        related_name="approved_programs",
        null=True,
        on_delete=fields.CASCADE,
        description="Документ",
    )

    class Meta:
        description = "Одобренные программы"


class ClassSchedule(BaseModel):
    id = fields.IntField(pk=True, description="Идентификатор")

    program_stream = fields.ForeignKeyField(
        "models.ProgramStream",
        related_name="class_schedules",
        null=True,
        on_delete=fields.CASCADE,
        description="Поток образовательной программы",
    )

    day_of_week = fields.IntField(null=True, description="День недели")
    start_time = fields.TimeField(null=True, description="Время начала")
    end_time = fields.TimeField(null=True, description="Время окончания")

    class Meta:
        description = "Время занятий потока образовательной программы"
