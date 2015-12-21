# -*- coding: utf-8 -*-

__author__ = 'Matthieu Gallet'


def is_admin(username):
    """
    >>> is_admin('myuser')
    False

    >>> is_admin('myuser_admin')
    True
    :param username:
    :type username:
    :return:
    :rtype:
    """
    return username.endswith('_admin')


def guess_name_components(display_name):
    """
    >>> guess_name_components('Matthieu GALLET')
    ('matthieu', 'GALLET')

    :param display_name:
    :type display_name:
    :return:
    :rtype:
    """
    if display_name is None:
        return None, None
    first_name_components = []
    last_name_components = []
    is_last_name = False
    for component in display_name.split():
        if component == component.upper() or is_last_name:
            is_last_name = True
            last_name_components.append(component)
        else:
            first_name_components.append(component)
    return ' '.join(first_name_components), ' '.join(last_name_components)


class Synchronizer(object):

    def get_ref_elements(self):
        raise NotImplementedError

    def get_copy_elements(self):
        raise NotImplementedError

    # noinspection PyMethodMayBeStatic
    def filter_ref_elements(self, ref_elements):
        return ref_elements

    # noinspection PyMethodMayBeStatic
    def filter_copy_elements(self, copy_elements):
        return copy_elements

    def synchronize(self):
        self.set_up()
        ref_elements = self.get_ref_elements()
        copy_elements = self.get_copy_elements()
        ref_dict = {self.get_ref_to_id(x): x for x in self.filter_ref_elements(ref_elements)}
        copy_dict = {self.get_copy_to_id(x): x for x in self.filter_copy_elements(copy_elements)}
        prepared_new_copy_elements = [self.prepare_new_copy_element(ref_element)
                                      for id_, ref_element in ref_dict.items() if id_ not in copy_dict]
        prepared_delete_copy_elements = [self.prepare_delete_copy_element(copy_element)
                                         for id_, copy_element in copy_dict.items() if id_ not in ref_dict]
        for id_, ref_element in ref_dict.items():
            if id_ in copy_dict:
                self.update_copy_element(copy_dict[id_], ref_element)
        self.delete_copy_elements(prepared_delete_copy_elements)
        self.create_copy_elements(prepared_new_copy_elements)
        self.tear_down()

    def set_up(self):
        pass

    def tear_down(self):
        pass

    def get_ref_to_id(self, ref_element):
        raise NotImplementedError

    def get_copy_to_id(self, copy_element):
        raise NotImplementedError

    def prepare_new_copy_element(self, ref_element):
        raise NotImplementedError

    def prepare_delete_copy_element(self, copy_element):
        raise NotImplementedError

    def update_copy_element(self, copy_element, ref_element):
        raise NotImplementedError

    def create_copy_elements(self, prepared_copy_elements):
        raise NotImplementedError

    def delete_copy_elements(self, prepared_copy_elements):
        raise NotImplementedError
