"""Behavior Module"""
#TODO: Come up with a better name!

import logging
import enum
import oh_behave

logger = logging.getLogger(__name__)

def print_node_decorator(func):
    """
    Returns decorator function that prints execution information
    """

    def func_decorator(self, *args, **kwargs):
        """See print_node_decorator documentation"""
        logger.info('Node %s.%s running', self.get_id(), func.__name__)

        ret = func(self, *args, **kwargs)

        msg = 'Node {0}.{1} finished.'.format(self.get_id(), func.__name__)
        if ret in oh_behave.ExecuteResult:
            msg += ' returns status \"{0}\"'.format(str(ret))
        logger.info(msg)

        return ret

    return func_decorator

class Node:
    """Base node class"""
    def __init__(self, *args, **kwargs):
        self._ident = kwargs.get('id', None)
        self.name = kwargs.get('name', None)
        if self._ident is None:
            raise oh_behave.MissingArgumentException(self, self.__init__, 'id')

    def get_id(self):
        """
        Returns the id representing the node's string
        """
        return self._ident

    @print_node_decorator
    def execute(self):
        """
        Wrapper with some common code for execution of nodes
        """
        ret = self._execute()
        return ret

    @print_node_decorator
    def failed(self):
        """
        Wrapper with some common code for execution of nodes
        """
        ret = self._failed()
        return ret

    @print_node_decorator
    def success(self):
        """
        Wrapper with some common code for success methods of nodes
        """
        ret = self._success()
        return ret

    def get_name(self):
        """
        Method to read the name variable
        """
        return self._name

    def _execute(self):
        """
        Abstract private method for executing the node

        Implementations should return an oh_behave.ExecuteResult
        """
        raise NotImplementedError(mod.ERR_ABSTRACT_CALL)

    def _failed(self):
        """
        Abstract method to run on node failure
        """
        raise NotImplementedError(mod.ERR_ABSTRACT_CALL)

    def _success(self):
        """
        Abstract method to run on node success
        """
        raise NotImplementedError(mod.ERR_ABSTRACT_CALL)

class NodeComposite(Node):
    """Abstract Base composite node class"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._children = []

    def addchild(self, childnode):
        """
        Wrapper with some common code for addchild methods of composite nodes
        """
        return self._addchild(childnode)
    def _addchild(self, childnode):
        """ Add a child to the composite node"""
        self._children.append(childnode)

class NodeSequence(NodeComposite):
    """Sequence node class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _success(self):
        pass

    def _failed(self):
        pass

    def _execute(self):
        """Execute the child nodes in a sequence"""

        if len(self._children) == 0:
            status = oh_behave.ExecuteResult.success
        else:
            firstnode = self._children[0]
            status = firstnode.execute()
            if status is oh_behave.ExecuteResult.success:
                firstnode.success()
                self._children.pop(0)
                if len(self._children) == 0:
                    status = oh_behave.ExecuteResult.success
                else:
                    status = oh_behave.ExecuteResult.ready

            elif status is oh_behave.ExecuteResult.failure:
                firstnode.failed()

        return status


class NodeSelector(NodeComposite):
    """Sequence node class"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _success(self):
        pass

    def _failed(self):
        pass

    def _execute(self):
        """Execute until one of the children succeed"""

        if len(self._children) == 0:
            status = oh_behave.ExecuteResult.failure
        else:
            firstnode = self._children[0]
            status = firstnode.execute()
            if status is oh_behave.ExecuteResult.failure:
                firstnode.failed()
                self._children.pop(0)
                if len(self._children) == 0:
                    status = oh_behave.ExecuteResult.failure
                else:
                    status = oh_behave.ExecuteResult.ready

            elif status is oh_behave.ExecuteResult.success:
                firstnode.success()

        return status

class NodeDecorator(Node):
    """Base Decorator, passes everything through"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._decoratee = kwargs['decoratee']
        except KeyError as e:
            raise oh_behave.MissingArgumentException(self, self.__init__, str(e))
    def set_decoratee(self, decoratee):
        """Set the node the decorator works on"""
        #TODO : Improve the output on this by adding a __str__ method to node
        logger.info('Decorator node id "%s" changing decorator to "%s"',
                self._ident, decoratee.get_id())
        self._decoratee = decoratee
    def _success(self):
        self._decoratee.success()

    def _failed(self):
        self._decoratee.failed()

    def _execute(self):
        return self._decoratee.execute()

class NodeDecoratorInvert(NodeDecorator):
    """Inverts execute result of child node"""
    def _execute(self):
        status = self._decoratee.execute()
        if status is oh_behave.ExecuteResult.success:
            status = oh_behave.ExecuteResult.failure
        elif status is oh_behave.ExecuteResult.failure:
            status = oh_behave.ExecuteResult.success
        return status

class NodeLeafAction(Node):
    """Node that runs runs an action"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            self._action = kwargs['action']
        except KeyError as e:
            raise oh_behave.MissingArgumentException(self, self.__init__, str(e))

    def _success(self):
        return self._action.success()

    def _failed(self):
        return self._action.failed()

    def _execute(self):
        return self._action.execute()



