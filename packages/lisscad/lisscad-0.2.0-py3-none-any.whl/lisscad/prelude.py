('Lisscad’s bundled macros.')

# hissp.macros.._macro_.prelude
__import__('builtins').exec(
  ('from itertools import *;from operator import *\n'
   'def engarde(xs,h,f,/,*a,**kw):\n'
   ' try:return f(*a,**kw)\n'
   ' except xs as e:return h(e)\n'
   'def enter(c,f,/,*a):\n'
   ' with c as C:return f(*a,C)\n'
   "class Ensue(__import__('collections.abc').abc.Generator):\n"
   ' send=lambda s,v:s.g.send(v);throw=lambda s,*x:s.g.throw(*x);F=0;X=();Y=[]\n'
   ' def __init__(s,p):s.p,s.g,s.n=p,s._(s),s.Y\n'
   ' def _(s,k,v=None):\n'
   "  while isinstance(s:=k,__class__) and not setattr(s,'sent',v):\n"
   '   try:k,y=s.p(s),s.Y;v=(yield from y)if s.F or y is s.n else(yield y)\n'
   '   except s.X as e:v=e\n'
   '  return k\n'
   "_macro_=__import__('types').SimpleNamespace()\n"
   "try: vars(_macro_).update(vars(__import__('hissp')._macro_))\n"
   'except ModuleNotFoundError: pass'),
  __import__('builtins').globals())

# defmacro
__import__('builtins').setattr(
  __import__('builtins').globals().get(
    ('_macro_')),
  'standard',
  # hissp.macros.._macro_.fun
  # hissp.macros.._macro_.let
  (
   lambda _Qzwfz72h4o__lambda=(lambda :
              (
                'lisscad.prelude.._macro_.progn',
                (
                  'lisscad.prelude.._macro_.prelude',
                  ),
                (
                  'builtins..exec',
                  "('from lisscad.vocab.base import *')",
                  (
                    'builtins..globals',
                    ),
                  ),
                (
                  'builtins..exec',
                  "('from lisscad.app import write')",
                  (
                    'builtins..globals',
                    ),
                  ),
                (
                  'builtins..exec',
                  "('from lisscad.data.other import Asset')",
                  (
                    'builtins..globals',
                    ),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'π',
                  'math..pi',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'τ',
                  'math..tau',
                  ),
                (
                  'builtins..delattr',
                  '_macro_',
                  (
                    'quote',
                    'QzPCENT_',
                    ),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzPCENT_',
                  'lisscad.op..background_dict',
                  ),
                (
                  'builtins..delattr',
                  '_macro_',
                  (
                    'quote',
                    'QzHASH_',
                    ),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzHASH_',
                  'lisscad.op..debug_set',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzBANG_',
                  'lisscad.vocab.base..root',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzSTAR_',
                  'lisscad.op..mul',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzET_',
                  'lisscad.vocab.base..intersection',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzPLUS_',
                  'lisscad.op..add',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzH_',
                  'lisscad.op..sub',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzSOL_',
                  'lisscad.op..div',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'first',
                  (
                    'functools..partial',
                    (
                      'operator..itemgetter',
                      (0),
                      ),
                    '',
                    ),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'second',
                  (
                    'functools..partial',
                    (
                      'operator..itemgetter',
                      (1),
                      ),
                    '',
                    ),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'third',
                  (
                    'functools..partial',
                    (
                      'operator..itemgetter',
                      (2),
                      ),
                    '',
                    ),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzDOLR_fa',
                  __import__('functools').partial(
                    __import__('lisscad.vocab.base',fromlist='*').special,
                    ('$fa')),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzDOLR_fn',
                  __import__('functools').partial(
                    __import__('lisscad.vocab.base',fromlist='*').special,
                    ('$fn')),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'QzDOLR_fs',
                  __import__('functools').partial(
                    __import__('lisscad.vocab.base',fromlist='*').special,
                    ('$fs')),
                  ),
                )
          ):
     ((
        *__import__('itertools').starmap(
           _Qzwfz72h4o__lambda.__setattr__,
           __import__('builtins').dict(
             __doc__=('Provide an OpenSCAD-like API with added consistency, safety and convenience.'),
             __name__='standard',
             __qualname__='_macro_.standard',
             __code__=_Qzwfz72h4o__lambda.__code__.replace(
                        co_name='standard')).items()),
        ),
      _Qzwfz72h4o__lambda)  [-1]
  )())

# defmacro
__import__('builtins').setattr(
  __import__('builtins').globals().get(
    ('_macro_')),
  'lisp',
  # hissp.macros.._macro_.fun
  # hissp.macros.._macro_.let
  (
   lambda _Qzwfz72h4o__lambda=(lambda :
              (
                'lisscad.prelude.._macro_.progn',
                (
                  'lisscad.prelude.._macro_.standard',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'callQzH_module',
                  (
                    'functools..partial',
                    'lisscad.vocab.base..module',
                    ':',
                    'lisscad.prelude..call',
                    True,
                    ),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'linearQzH_extrude',
                  (
                    'functools..partial',
                    'lisscad.vocab.base..extrude',
                    ':',
                    'lisscad.prelude..rotate',
                    False,
                    ),
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'rotateQzH_extrude',
                  (
                    'functools..partial',
                    'lisscad.vocab.base..extrude',
                    ':',
                    'lisscad.prelude..rotate',
                    True,
                    ),
                  ),
                )
          ):
     ((
        *__import__('itertools').starmap(
           _Qzwfz72h4o__lambda.__setattr__,
           __import__('builtins').dict(
             __doc__=('Provide unambiguous aliases in kebab case, traditionally idiomatic for '
                      'Lisp.\n'
                      '  This is a superset of the standard prelude.'),
             __name__='lisp',
             __qualname__='_macro_.lisp',
             __code__=_Qzwfz72h4o__lambda.__code__.replace(
                        co_name='lisp')).items()),
        ),
      _Qzwfz72h4o__lambda)  [-1]
  )())

# defmacro
__import__('builtins').setattr(
  __import__('builtins').globals().get(
    ('_macro_')),
  'english',
  # hissp.macros.._macro_.fun
  # hissp.macros.._macro_.let
  (
   lambda _Qzwfz72h4o__lambda=(lambda :
              (
                'lisscad.prelude.._macro_.progn',
                (
                  'lisscad.prelude.._macro_.lisp',
                  ),
                (
                  'builtins..exec',
                  "('from lisscad.vocab.english import *')",
                  (
                    'builtins..globals',
                    ),
                  ),
                )
          ):
     ((
        *__import__('itertools').starmap(
           _Qzwfz72h4o__lambda.__setattr__,
           __import__('builtins').dict(
             __doc__=('Patch over parts of the OpenSCAD vocabulary with more literal English.\n'
                      '  This is a superset of the lisp prelude.'),
             __name__='english',
             __qualname__='_macro_.english',
             __code__=_Qzwfz72h4o__lambda.__code__.replace(
                        co_name='english')).items()),
        ),
      _Qzwfz72h4o__lambda)  [-1]
  )())

# defmacro
__import__('builtins').setattr(
  __import__('builtins').globals().get(
    ('_macro_')),
  'util',
  # hissp.macros.._macro_.fun
  # hissp.macros.._macro_.let
  (
   lambda _Qzwfz72h4o__lambda=(lambda :
              (
                'lisscad.prelude.._macro_.progn',
                (
                  'lisscad.prelude.._macro_.define',
                  'slidingQzH_hull',
                  'lisscad.vocab.util..sliding_hull',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'radiate',
                  'lisscad.vocab.util..radiate',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'round',
                  'lisscad.vocab.util..round',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'wafer',
                  'lisscad.vocab.util..wafer',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'unionQzH_map',
                  'lisscad.vocab.util..union_map',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'rotationalQzH_symmetry',
                  'lisscad.vocab.util..rotational_symmetry',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'bilateralQzH_symmetryQzH_x',
                  'lisscad.vocab.util..bilateral_symmetry_x',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'bilateralQzH_symmetryQzH_y',
                  'lisscad.vocab.util..bilateral_symmetry_y',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'bilateralQzH_symmetryQzH_z',
                  'lisscad.vocab.util..bilateral_symmetry_z',
                  ),
                (
                  'lisscad.prelude.._macro_.define',
                  'bilateralQzH_symmetryQzH_xy',
                  'lisscad.vocab.util..bilateral_symmetry_xy',
                  ),
                )
          ):
     ((
        *__import__('itertools').starmap(
           _Qzwfz72h4o__lambda.__setattr__,
           __import__('builtins').dict(
             __doc__=('Provide higher-level utilities only.'),
             __name__='util',
             __qualname__='_macro_.util',
             __code__=_Qzwfz72h4o__lambda.__code__.replace(
                        co_name='util')).items()),
        ),
      _Qzwfz72h4o__lambda)  [-1]
  )())

# defmacro
__import__('builtins').setattr(
  __import__('builtins').globals().get(
    ('_macro_')),
  'englishQzH_util',
  # hissp.macros.._macro_.fun
  # hissp.macros.._macro_.let
  (
   lambda _Qzwfz72h4o__lambda=(lambda :
              (
                'lisscad.prelude.._macro_.progn',
                (
                  'lisscad.prelude.._macro_.english',
                  ),
                (
                  'lisscad.prelude.._macro_.util',
                  ),
                )
          ):
     ((
        *__import__('itertools').starmap(
           _Qzwfz72h4o__lambda.__setattr__,
           __import__('builtins').dict(
             __doc__=('Provide higher-level utilities with English-language vocabulary.'),
             __name__='englishQzH_util',
             __qualname__='_macro_.englishQzH_util',
             __code__=_Qzwfz72h4o__lambda.__code__.replace(
                        co_name='englishQzH_util')).items()),
        ),
      _Qzwfz72h4o__lambda)  [-1]
  )())