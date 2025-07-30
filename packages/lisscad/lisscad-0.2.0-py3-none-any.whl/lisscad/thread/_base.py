# lisscad.prelude.._macro_.englishQzH_util
# lisscad.prelude.._macro_.progn
(# lisscad.prelude.._macro_.english
 # lisscad.prelude.._macro_.progn
 (# lisscad.prelude.._macro_.lisp
  # lisscad.prelude.._macro_.progn
  (# lisscad.prelude.._macro_.standard
   # lisscad.prelude.._macro_.progn
   (# lisscad.prelude.._macro_.prelude
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
      __import__('builtins').globals()),
    __import__('builtins').exec(
      ('from lisscad.vocab.base import *'),
      __import__('builtins').globals()),
    __import__('builtins').exec(
      ('from lisscad.app import write'),
      __import__('builtins').globals()),
    __import__('builtins').exec(
      ('from lisscad.data.other import Asset'),
      __import__('builtins').globals()),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      π=__import__('math').pi),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      τ=__import__('math').tau),
    __import__('builtins').delattr(
      _macro_,
      'QzPCENT_'),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzPCENT_=__import__('lisscad.op',fromlist='*').background_dict),
    __import__('builtins').delattr(
      _macro_,
      'QzHASH_'),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzHASH_=__import__('lisscad.op',fromlist='*').debug_set),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzBANG_=__import__('lisscad.vocab.base',fromlist='*').root),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzSTAR_=__import__('lisscad.op',fromlist='*').mul),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzET_=__import__('lisscad.vocab.base',fromlist='*').intersection),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzPLUS_=__import__('lisscad.op',fromlist='*').add),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzH_=__import__('lisscad.op',fromlist='*').sub),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzSOL_=__import__('lisscad.op',fromlist='*').div),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      first=__import__('functools').partial(
              __import__('operator').itemgetter(
                (0)),
              )),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      second=__import__('functools').partial(
               __import__('operator').itemgetter(
                 (1)),
               )),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      third=__import__('functools').partial(
              __import__('operator').itemgetter(
                (2)),
              )),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzDOLR_fa=# functools.partial(<function special at 0x710ce0515fc0>, '$fa')
                __import__('pickle').loads(b'cfunctools\npartial\n(clisscad.vocab.base\nspecial\np0\ntR(g0\n(V$fa\nt(dNtb.')),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzDOLR_fn=# functools.partial(<function special at 0x710ce0515fc0>, '$fn')
                __import__('pickle').loads(b'cfunctools\npartial\n(clisscad.vocab.base\nspecial\np0\ntR(g0\n(V$fn\nt(dNtb.')),
    # lisscad.prelude.._macro_.define
    __import__('builtins').globals().update(
      QzDOLR_fs=# functools.partial(<function special at 0x710ce0515fc0>, '$fs')
                __import__('pickle').loads(b'cfunctools\npartial\n(clisscad.vocab.base\nspecial\np0\ntR(g0\n(V$fs\nt(dNtb.')))  [-1],
   # lisscad.prelude.._macro_.define
   __import__('builtins').globals().update(
     callQzH_module=__import__('functools').partial(
                      __import__('lisscad.vocab.base',fromlist='*').module,
                      call=True)),
   # lisscad.prelude.._macro_.define
   __import__('builtins').globals().update(
     linearQzH_extrude=__import__('functools').partial(
                         __import__('lisscad.vocab.base',fromlist='*').extrude,
                         rotate=False)),
   # lisscad.prelude.._macro_.define
   __import__('builtins').globals().update(
     rotateQzH_extrude=__import__('functools').partial(
                         __import__('lisscad.vocab.base',fromlist='*').extrude,
                         rotate=True)))  [-1],
  __import__('builtins').exec(
    ('from lisscad.vocab.english import *'),
    __import__('builtins').globals()))  [-1],
 # lisscad.prelude.._macro_.util
 # lisscad.prelude.._macro_.progn
 (# lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    slidingQzH_hull=__import__('lisscad.vocab.util',fromlist='*').sliding_hull),
  # lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    radiate=__import__('lisscad.vocab.util',fromlist='*').radiate),
  # lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    round=__import__('lisscad.vocab.util',fromlist='*').round),
  # lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    wafer=__import__('lisscad.vocab.util',fromlist='*').wafer),
  # lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    unionQzH_map=__import__('lisscad.vocab.util',fromlist='*').union_map),
  # lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    rotationalQzH_symmetry=__import__('lisscad.vocab.util',fromlist='*').rotational_symmetry),
  # lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    bilateralQzH_symmetryQzH_x=__import__('lisscad.vocab.util',fromlist='*').bilateral_symmetry_x),
  # lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    bilateralQzH_symmetryQzH_y=__import__('lisscad.vocab.util',fromlist='*').bilateral_symmetry_y),
  # lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    bilateralQzH_symmetryQzH_z=__import__('lisscad.vocab.util',fromlist='*').bilateral_symmetry_z),
  # lisscad.prelude.._macro_.define
  __import__('builtins').globals().update(
    bilateralQzH_symmetryQzH_xy=__import__('lisscad.vocab.util',fromlist='*').bilateral_symmetry_xy))  [-1])  [-1]

# define
__import__('builtins').globals().update(
  _distanceQzH_toQzH_end=(lambda length:
                             (lambda coordinate:
                                 min(
                                   coordinate,
                                   QzH_(
                                     length,
                                     coordinate))
                             )
                         ))

# define
__import__('builtins').globals().update(
  _flatQzH_endQzH_z=(
                     lambda limit,
                            overshoot=(0):
                        # let
                        (
                         lambda floor=QzH_(
                                  overshoot),
                                ceiling=QzPLUS_(
                                  limit,
                                  overshoot):
                            (lambda coordinate:
                                max(
                                  floor,
                                  min(
                                    ceiling,
                                    coordinate))
                            )
                        )()
                    ))