(import
  ast
  itertools [dropwhile]
  hyrule [pformat]
  packaging.version [Version])

(eval-and-compile (setv
  cat hy.I.itertools.chain.from-iterable))

(eval-and-compile (defn S [x]
  (cond
    ; Use Unicode mincing for Python identifiers not expressible as Hy
    ; symbols.
    (= x "Inf") '𝐈𝐧𝐟
    (= x "NaN") '𝐍𝐚𝐍
    True        (hy.models.Symbol x))))


(defn ast-to-models [x [allow-unimplemented False]]
  "Given a Python `ast` object `x`, return a `list` of Hy model
  objects (or possibly just one model, if the input wasn't one of the
  usual top-level `ast` classes).

  By default, unimplemented AST nodes raise `NotImplementedError`. If
  `allow_unimplemented` is true, these nodes are replaced with a
  `hy.models.Tuple` where the first element is the symbol
  `NotImplemented`, and the second is the node type name as a
  `hy.models.String`."

  (defmacro T [arg]
    ; "T" is for "translate".
    `(ast-to-models ~arg allow-unimplemented))

  (defn Tn [arg]
    (if (is arg None) 'None (T arg)))

  (defn digest-arg [xd]
    (setv [x default] xd)
    (setv a (S x.arg))
    (when default
      (setv a `[~a ~(T default)]))
    (if (or x.annotation x.type-comment)
      `(annotate ~a ~(T (or x.annotation x.type-comment)))
      a))

  (when (isinstance x list)
    (return (lfor
      e x
      :if (not (isinstance e ast.Pass))
      (T e))))

  (do-mac

    (setv translation-table (list (.items '{

      [Module Interactive Expression]
        (T x.body)

      [FunctionDef AsyncFunctionDef]
        `(defn
          ~@(when (isinstance x ast.AsyncFunctionDef)
            [:async])
          ~@(when x.decorator-list
            `[~(T x.decorator-list)])
          ~@(when x.type-params
            [:tp (T x.type-params)])
          ~(if (or x.returns x.type-comment)
            `(annotate ~(S x.name) ~(T (or x.returns x.type-comment)))
            (S x.name))
          ~(T x.args)
          ~@(T x.body))

      ClassDef
        `(defclass
          ~@(when x.decorator-list
            `[~@(T x.decorator-list)])
          ~@(when x.type-params
            [:tp (T x.type-params)])
          ~(S x.name)
          [~@(T x.bases)]
          ~@(T x.body))

      [Return Yield Await]
        `(
          ~(S (.lower (. (type x) __name__)))
          ~@(when x.value [(T x.value)]))
      Delete
        `(del ~@(T x.targets))
      Assign
        `(setv ~@(cond
          (= (len x.targets) 1) [
            ; This is a non-chained assignment.
            (T (get x.targets 0))
            (T x.value)]
          (>= (Version hy.last-version) (Version "1.2")) [
            ; We have a sufficiently new Hy for chained assignment.
            :chain
            (hy.models.List (T x.targets))
            (T x.value)]
          True [
            ; Represent a chained assignment like   `a = b = c = d`
            ; as                                    `(setv [a b c] (* [d] 3))`
            (hy.models.List (T x.targets))
            `(* [~(T x.value)] ~(hy.models.Integer (len x.targets)))]))
      AugAssign
        `(
          ~(S (+ (T x.op) '=))
          ~(T x.target)
          ~(T x.value))
      AnnAssign
        (do
          (setv a `(annotate ~(T x.target) ~(T x.annotation)))
          (if x.value
            `(setv ~a ~(T x.value))
            a))

      [For AsyncFor]
        `(for
          [
            ~@(when (isinstance x ast.AsyncFor) [:async])
            ~(T x.target)
            ~(T x.iter)]
          ~@(T x.body)
          ~@(when x.orelse
            [`(else ~@(T x.orelse))]))

      While
        `(while ~(T x.test)
          ~@(T x.body)
          ~@(when x.orelse
            [`(else ~@(T x.orelse))]))
      If
        (if x.orelse
          `(if ~(T x.test)
            (do ~@(T x.body))
            (do ~@(T x.orelse)))
          `(when ~(T x.test)
            ~@(T x.body)))

      [With AsyncWith]
        `(with
          [~@(cat (gfor
            models (T x.items)
            (if (isinstance x ast.AsyncWith)
              [:async #* models]
              models)))]
          ~@(T x.body))

      Raise
        `(raise
          ~@(when x.exc [(T x.exc)])
          ~@(when x.cause [:from (T x.cause)]))

      Try
        `(try
          ~@(T x.body)
          ~@(T x.handlers)
          ~@(when x.orelse
            [`(else ~@(T x.orelse))])
          ~@(when x.finalbody
            [`(finally ~@(T x.finalbody))]))

      Assert
        `(assert ~(T x.test) ~@(when x.msg [(T x.msg)]))
      Import
        `(import ~@(cat (T x.names)))
      ImportFrom
        `(import
          ~(hy.read (+ (* "." x.level) (or x.module "")))
          ~(if (and (= (len x.names) 1) (= (. x names [0] name) "*"))
            '*
            `[~@(cat (T x.names))]))
      Global
        `(global ~@(map S x.names))
      Nonlocal
        `(nonlocal ~@(map S x.names))
      Expr
        (T x.value)

      Pass
        ; We try to skip `Pass` nodes, so this should only come up if
        ; e.g. the user gives an unadorned `Pass` node to
        ; `ast-to-models`.
        'None
      Break
        '(break)
      Continue
        '(continue)

      BoolOp
        `(~(T x.op) ~@(T x.values))
      NamedExpr
        `(setx ~(T x.target) ~(T x.value))
      BinOp
        `(~(T x.op) ~(T x.left) ~(T x.right))
      UnaryOp
        (if (and
            (isinstance x.op ast.USub)
            (isinstance x.operand ast.Constant)
            (isinstance x.operand.value hy.I.numbers.Number))
          ; Ensure `-2` becomes `-2` and not `(- 2)`.
          (hy.as-model (- x.operand.value))
          `(~(T x.op) ~(T x.operand)))
      Lambda
        `(fn ~(T x.args) ~(T x.body))
      IfExp
        `(if ~(T x.test) ~(T x.body) ~(T x.orelse))
      Dict
        `{~@(cat (gfor
          [k v] (zip x.keys x.values)
          (if (is k None)
            ; `v` is a mapping to unpack.
            [`(unpack-mapping ~(T v))]
            ; Otherwise, we have a normal key-value pair.
            [(T k) (T v)])))}
      Set
        `#{~@(T x.elts)}
      [ListComp SetComp DictComp GeneratorExp]
         `(
            ~(S (+ (.lower (. (type x) __name__ [0])) "for"))
            ~@(cat (T x.generators))
            ~@(if (isinstance x ast.DictComp)
              [(T x.key) (T x.value)]
              [(T x.elt)]))
      YieldFrom
        `(yield :from ~(T x.value))
      Compare
        (if (= (len (set x.ops)) 1)
          ; If only one distinct operator is used, then we can use a
          ; plain comparison form.
          `(~(T (get x.ops 0)) ~(T x.left) ~@(T x.comparators))
          ; Otherwise, we need `chainc`.
          `(chainc ~(T x.left) ~@(cat (gfor
            [op y] (zip x.ops x.comparators)
            [(T op) (T y)]))))
      Call
        `(~(T x.func) ~@(T x.args) ~@(cat (T x.keywords)))

      FormattedValue
        (hy.models.FComponent
          #((T x.value) #* (if x.format-spec [(T x.format-spec)] []))
          :conversion (when (!= x.conversion -1) (chr x.conversion)))
      JoinedStr
        (if (and
            (= (len x.values) 1)
            (isinstance (get x.values 0) ast.Constant))
          (T (get x.values 0))
          (hy.models.FString (T x.values)))

      Constant
        (if (= x.value ...)
          '...
          (hy.as-model x.value))
      Attribute
        `(. ~(T x.value) ~(S x.attr))
      Subscript
        (if (isinstance x.slice ast.Slice)
          `(cut ~(T x.value)
            ~@(cond
              (and x.slice.upper (not (or x.slice.lower x.slice.step)))
                [(T x.slice.upper)]
              (and x.slice.lower (not (or x.slice.upper x.slice.step)))
                [(T x.slice.lower) 'None]
              True
                (reversed (list (dropwhile
                  (fn [x] (= x 'None))
                  (map Tn [x.slice.step x.slice.upper x.slice.lower]))))))
          `(get ~(T x.value) ~(T x.slice)))
      Starred
        `(unpack-iterable ~(T x.value))
      Name
        (S x.id)
      List
        `[~@(T x.elts)]
      Tuple
        `#(~@(T x.elts))

      Slice
        `(hy.I.builtins.slice ~(Tn x.lower) ~(Tn x.upper) ~(Tn x.step))

      comprehension
        `[
          ~@(when x.is-async [:async])
          ~(T x.target)
          ~(T x.iter)
          ~@(cat (gfor
            iffy x.ifs
            [:if (T iffy)]))]

      ExceptHandler
        `(except
          [
            ~@(when x.name [(S x.name)])
            ~@(when x.type [(T x.type)])]
          ~@(T x.body))

      arguments
        (do
          ; Augment `posonlyargs` and `args` with their corresponding default
          ; values in `defaults`.
          (setv posonlyargs (lfor  a x.posonlyargs  [a None]))
          (setv args (lfor  a x.args  [a None]))
          (for [[a v] (zip
              (cut (+ posonlyargs args) (len x.defaults) None)
              x.defaults)]
            (setv (get a 1) v))
          ; Likewise `kwonlyargs`.
          (setv kwonlyargs (list (zip x.kwonlyargs x.kw-defaults)))
          ; Construct the final lambda list.
         `[
           ~@(map digest-arg posonlyargs)
           ~@(when posonlyargs [(if x.vararg
             `(unpack-iterable ~(digest-arg [x.vararg None]))
             '/)])
           ~@(map digest-arg args)
           ~@(when (and (not posonlyargs) x.vararg)
             [`(unpack-iterable ~(digest-arg [x.vararg None]))])
           ~@(when (and kwonlyargs (not x.vararg))
             ['*])
           ~@(map digest-arg kwonlyargs)
           ~@(when x.kwarg
             [`(unpack-mapping ~(digest-arg [x.kwarg None]))])])

      arg
        (raise (ValueError "Can't happen (all `arg` nodes should have been caught earlier)"))
      keyword
        (if (is x.arg None)
           [`(unpack-mapping ~(T x.value))]
           [(hy.models.Keyword x.arg) (T x.value)])

      alias
        (do
          (setv name (if (in "." x.name)
            `(. ~@(map S (.split x.name ".")))
            (S x.name)))
          (if x.asname
            #(name :as (S x.asname))
            #(name)))

      withitem
        [
          (if x.optional-vars (T x.optional-vars) '_)
          (T x.context-expr)]})))

    ; Add operators to the translation table.
    (setv unpythonic-ops (dict (.items '{
      ; Operators spelled differently from Python.
      Eq     =
      Invert bnot
      IsNot  is-not
      NotIn  not-in})))
    (setv u hy.I.ast._Unparser)
    (for [[k v] (.items
        {#** u.unop #** u.binop #** u.cmpops #** u.boolops})]
      (setv k (S k))
      (.append translation-table #(
        k
        `'~(if (in k unpythonic-ops)
          (get unpythonic-ops k)
          (S v)))))

    ; Use the translation table to build a big `cond`.
    `(cond

      ~@(cat (gfor
        [k v] translation-table
        `[
          (isinstance x ~(hy.models.Tuple (gfor
            sym (if (isinstance k hy.models.List) k [k])
            `(. ast ~sym))))
          ~v]))

      (isinstance x ast.AST)
        (if allow-unimplemented
          `#(NotImplemented ~(hy.models.String (str (type x))))
          (raise (NotImplementedError f"Unimplemented `ast` node type: {(type x)}")))

      True
        (raise (TypeError f"Not an `ast` node: {x}")))))


(defn ast-to-text [x [allow-unimplemented False]]
  "Call `ast_to_models` and then return Hy source text from the models."
  (+
    (.join "\n" (gfor
      model (ast-to-models x allow-unimplemented)
      (.removeprefix (pformat model) "'")))
    "\n"))
