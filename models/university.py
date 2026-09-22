class University:
    def __init__(self, uni_id, name, domain, plan='basic', is_active=True):
        self.id = uni_id
        self.name = name
        self.domain = domain
        self.plan = plan
        self.is_active = is_active
