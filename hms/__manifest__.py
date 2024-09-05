{
    'name':'Hospital M System',
    'summary':'',
    'description':'hospital management system',
    'author':'esraa koryem',
    'category':'productivity',
    'version':'16.0.0.1.0',
    'depends':[
        'base',
        'crm'
    ],
    'application': True,
    'data':[
        'security/security.xml',
        # 'security/user_manger_group.xml',
        'security/ir.model.access.csv',
        'views/base_menus.xml',
        'views/patient_view.xml',
        'views/department_view.xml',
        'views/doctor_view.xml',
        'views/customer_view.xml',
        'report/patient_print.xml',
    ]
}