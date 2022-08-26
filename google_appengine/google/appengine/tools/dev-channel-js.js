(function(){/*

 Copyright The Closure Library Authors.
 SPDX-License-Identifier: Apache-2.0
*/
var $jscomp = $jscomp || {};
$jscomp.scope = {};
$jscomp.createTemplateTagFirstArg = function(arrayStrings) {
  return arrayStrings.raw = arrayStrings;
};
$jscomp.createTemplateTagFirstArgWithRaw = function(arrayStrings, rawArrayStrings) {
  arrayStrings.raw = rawArrayStrings;
  return arrayStrings;
};
$jscomp.arrayIteratorImpl = function(array) {
  var index = 0;
  return function() {
    return index < array.length ? {done:!1, value:array[index++],} : {done:!0};
  };
};
$jscomp.arrayIterator = function(array) {
  return {next:$jscomp.arrayIteratorImpl(array)};
};
$jscomp.makeIterator = function(iterable) {
  var iteratorFunction = "undefined" != typeof Symbol && Symbol.iterator && iterable[Symbol.iterator];
  return iteratorFunction ? iteratorFunction.call(iterable) : $jscomp.arrayIterator(iterable);
};
$jscomp.ASSUME_ES5 = !1;
$jscomp.ASSUME_NO_NATIVE_MAP = !1;
$jscomp.ASSUME_NO_NATIVE_SET = !1;
$jscomp.SIMPLE_FROUND_POLYFILL = !1;
$jscomp.ISOLATE_POLYFILLS = !1;
$jscomp.FORCE_POLYFILL_PROMISE = !1;
$jscomp.FORCE_POLYFILL_PROMISE_WHEN_NO_UNHANDLED_REJECTION = !1;
$jscomp.defineProperty = $jscomp.ASSUME_ES5 || "function" == typeof Object.defineProperties ? Object.defineProperty : function(target, property, descriptor) {
  if (target == Array.prototype || target == Object.prototype) {
    return target;
  }
  target[property] = descriptor.value;
  return target;
};
$jscomp.getGlobal = function(passedInThis) {
  for (var possibleGlobals = ["object" == typeof globalThis && globalThis, passedInThis, "object" == typeof window && window, "object" == typeof self && self, "object" == typeof global && global,], i = 0; i < possibleGlobals.length; ++i) {
    var maybeGlobal = possibleGlobals[i];
    if (maybeGlobal && maybeGlobal.Math == Math) {
      return maybeGlobal;
    }
  }
  throw Error("Cannot find global object");
};
$jscomp.global = $jscomp.getGlobal(this);
$jscomp.IS_SYMBOL_NATIVE = "function" === typeof Symbol && "symbol" === typeof Symbol("x");
$jscomp.TRUST_ES6_POLYFILLS = !$jscomp.ISOLATE_POLYFILLS || $jscomp.IS_SYMBOL_NATIVE;
$jscomp.polyfills = {};
$jscomp.propertyToPolyfillSymbol = {};
$jscomp.POLYFILL_PREFIX = "$jscp$";
$jscomp.polyfill = function(target, polyfill, fromLang, toLang) {
  polyfill && ($jscomp.ISOLATE_POLYFILLS ? $jscomp.polyfillIsolated(target, polyfill, fromLang, toLang) : $jscomp.polyfillUnisolated(target, polyfill, fromLang, toLang));
};
$jscomp.polyfillUnisolated = function(target, polyfill) {
  for (var obj = $jscomp.global, split = target.split("."), i = 0; i < split.length - 1; i++) {
    var key = split[i];
    if (!(key in obj)) {
      return;
    }
    obj = obj[key];
  }
  var property = split[split.length - 1], orig = obj[property], impl = polyfill(orig);
  impl != orig && null != impl && $jscomp.defineProperty(obj, property, {configurable:!0, writable:!0, value:impl});
};
$jscomp.polyfillIsolated = function(target, polyfill, fromLang) {
  var split = target.split("."), isSimpleName = 1 === split.length, root = split[0];
  var ownerObject = !isSimpleName && root in $jscomp.polyfills ? $jscomp.polyfills : $jscomp.global;
  for (var i = 0; i < split.length - 1; i++) {
    var key = split[i];
    if (!(key in ownerObject)) {
      return;
    }
    ownerObject = ownerObject[key];
  }
  var property = split[split.length - 1], nativeImpl = $jscomp.IS_SYMBOL_NATIVE && "es6" === fromLang ? ownerObject[property] : null, impl = polyfill(nativeImpl);
  if (null != impl) {
    if (isSimpleName) {
      $jscomp.defineProperty($jscomp.polyfills, property, {configurable:!0, writable:!0, value:impl});
    } else if (impl !== nativeImpl) {
      if (void 0 === $jscomp.propertyToPolyfillSymbol[property]) {
        var BIN_ID = 1E9 * Math.random() >>> 0;
        $jscomp.propertyToPolyfillSymbol[property] = $jscomp.IS_SYMBOL_NATIVE ? $jscomp.global.Symbol(property) : $jscomp.POLYFILL_PREFIX + BIN_ID + "$" + property;
      }
      var obfuscatedName = $jscomp.propertyToPolyfillSymbol[property];
      $jscomp.defineProperty(ownerObject, obfuscatedName, {configurable:!0, writable:!0, value:impl});
    }
  }
};
$jscomp.underscoreProtoCanBeSet = function() {
  var x = {a:!0}, y = {};
  try {
    return y.__proto__ = x, y.a;
  } catch (e) {
  }
  return !1;
};
$jscomp.setPrototypeOf = $jscomp.TRUST_ES6_POLYFILLS && "function" == typeof Object.setPrototypeOf ? Object.setPrototypeOf : $jscomp.underscoreProtoCanBeSet() ? function(target, proto) {
  target.__proto__ = proto;
  if (target.__proto__ !== proto) {
    throw new TypeError(target + " is not extensible");
  }
  return target;
} : null;
$jscomp.generator = {};
$jscomp.generator.ensureIteratorResultIsObject_ = function(result) {
  if (!(result instanceof Object)) {
    throw new TypeError("Iterator result " + result + " is not an object");
  }
};
$jscomp.generator.Context = function() {
  this.isRunning_ = !1;
  this.yieldAllIterator_ = null;
  this.yieldResult = void 0;
  this.nextAddress = 1;
  this.finallyAddress_ = this.catchAddress_ = 0;
  this.finallyContexts_ = this.abruptCompletion_ = null;
};
$jscomp.generator.Context.prototype.start_ = function() {
  if (this.isRunning_) {
    throw new TypeError("Generator is already running");
  }
  this.isRunning_ = !0;
};
$jscomp.generator.Context.prototype.stop_ = function() {
  this.isRunning_ = !1;
};
$jscomp.generator.Context.prototype.jumpToErrorHandler_ = function() {
  this.nextAddress = this.catchAddress_ || this.finallyAddress_;
};
$jscomp.generator.Context.prototype.next_ = function(value) {
  this.yieldResult = value;
};
$jscomp.generator.Context.prototype.throw_ = function(e) {
  this.abruptCompletion_ = {exception:e, isException:!0};
  this.jumpToErrorHandler_();
};
$jscomp.generator.Context.prototype.return = function(value) {
  this.abruptCompletion_ = {return:value};
  this.nextAddress = this.finallyAddress_;
};
$jscomp.generator.Context.prototype.yield = function(value, resumeAddress) {
  this.nextAddress = resumeAddress;
  return {value:value};
};
$jscomp.generator.Context.prototype.jumpTo = function(nextAddress) {
  this.nextAddress = nextAddress;
};
$jscomp.generator.Context.prototype.setFinallyBlock = function(finallyAddress) {
  this.catchAddress_ = 0;
  this.finallyAddress_ = finallyAddress || 0;
};
$jscomp.generator.Context.prototype.enterFinallyBlock = function(nextCatchAddress, nextFinallyAddress, finallyDepth) {
  finallyDepth ? this.finallyContexts_[finallyDepth] = this.abruptCompletion_ : this.finallyContexts_ = [this.abruptCompletion_];
  this.catchAddress_ = nextCatchAddress || 0;
  this.finallyAddress_ = nextFinallyAddress || 0;
};
$jscomp.generator.Context.prototype.leaveFinallyBlock = function(nextAddress, finallyDepth) {
  var preservedContext = this.finallyContexts_.splice(finallyDepth || 0)[0], abruptCompletion = this.abruptCompletion_ = this.abruptCompletion_ || preservedContext;
  if (abruptCompletion) {
    if (abruptCompletion.isException) {
      return this.jumpToErrorHandler_();
    }
    void 0 != abruptCompletion.jumpTo && this.finallyAddress_ < abruptCompletion.jumpTo ? (this.nextAddress = abruptCompletion.jumpTo, this.abruptCompletion_ = null) : this.nextAddress = this.finallyAddress_;
  } else {
    this.nextAddress = nextAddress;
  }
};
$jscomp.generator.Context.PropertyIterator = function(object) {
  this.properties_ = [];
  for (var property in object) {
    this.properties_.push(property);
  }
  this.properties_.reverse();
};
$jscomp.generator.Engine_ = function(program) {
  this.context_ = new $jscomp.generator.Context();
  this.program_ = program;
};
$jscomp.generator.Engine_.prototype.next_ = function(value) {
  this.context_.start_();
  if (this.context_.yieldAllIterator_) {
    return this.yieldAllStep_(this.context_.yieldAllIterator_.next, value, this.context_.next_);
  }
  this.context_.next_(value);
  return this.nextStep_();
};
$jscomp.generator.Engine_.prototype.return_ = function(value) {
  this.context_.start_();
  var yieldAllIterator = this.context_.yieldAllIterator_;
  if (yieldAllIterator) {
    var returnFunction = "return" in yieldAllIterator ? yieldAllIterator["return"] : function(v) {
      return {value:v, done:!0};
    };
    return this.yieldAllStep_(returnFunction, value, this.context_.return);
  }
  this.context_.return(value);
  return this.nextStep_();
};
$jscomp.generator.Engine_.prototype.throw_ = function(exception) {
  this.context_.start_();
  if (this.context_.yieldAllIterator_) {
    return this.yieldAllStep_(this.context_.yieldAllIterator_["throw"], exception, this.context_.next_);
  }
  this.context_.throw_(exception);
  return this.nextStep_();
};
$jscomp.generator.Engine_.prototype.yieldAllStep_ = function(action, value, nextAction) {
  try {
    var result = action.call(this.context_.yieldAllIterator_, value);
    $jscomp.generator.ensureIteratorResultIsObject_(result);
    if (!result.done) {
      return this.context_.stop_(), result;
    }
    var resultValue = result.value;
  } catch (e) {
    return this.context_.yieldAllIterator_ = null, this.context_.throw_(e), this.nextStep_();
  }
  this.context_.yieldAllIterator_ = null;
  nextAction.call(this.context_, resultValue);
  return this.nextStep_();
};
$jscomp.generator.Engine_.prototype.nextStep_ = function() {
  for (; this.context_.nextAddress;) {
    try {
      var yieldValue = this.program_(this.context_);
      if (yieldValue) {
        return this.context_.stop_(), {value:yieldValue.value, done:!1};
      }
    } catch (e) {
      this.context_.yieldResult = void 0, this.context_.throw_(e);
    }
  }
  this.context_.stop_();
  if (this.context_.abruptCompletion_) {
    var abruptCompletion = this.context_.abruptCompletion_;
    this.context_.abruptCompletion_ = null;
    if (abruptCompletion.isException) {
      throw abruptCompletion.exception;
    }
    return {value:abruptCompletion.return, done:!0};
  }
  return {value:void 0, done:!0};
};
$jscomp.generator.Generator_ = function(engine) {
  this.next = function(opt_value) {
    return engine.next_(opt_value);
  };
  this.throw = function(exception) {
    return engine.throw_(exception);
  };
  this.return = function(value) {
    return engine.return_(value);
  };
  this[Symbol.iterator] = function() {
    return this;
  };
};
$jscomp.generator.createGenerator = function(generator, program) {
  var result = new $jscomp.generator.Generator_(new $jscomp.generator.Engine_(program));
  $jscomp.setPrototypeOf && generator.prototype && $jscomp.setPrototypeOf(result, generator.prototype);
  return result;
};
$jscomp.asyncExecutePromiseGenerator = function(generator) {
  function passValueToGenerator(value) {
    return generator.next(value);
  }
  function passErrorToGenerator(error) {
    return generator.throw(error);
  }
  return new Promise(function(resolve, reject) {
    function handleGeneratorRecord(genRec) {
      genRec.done ? resolve(genRec.value) : Promise.resolve(genRec.value).then(passValueToGenerator, passErrorToGenerator).then(handleGeneratorRecord, reject);
    }
    handleGeneratorRecord(generator.next());
  });
};
$jscomp.asyncExecutePromiseGeneratorFunction = function(generatorFunction) {
  return $jscomp.asyncExecutePromiseGenerator(generatorFunction());
};
$jscomp.asyncExecutePromiseGeneratorProgram = function(program) {
  return $jscomp.asyncExecutePromiseGenerator(new $jscomp.generator.Generator_(new $jscomp.generator.Engine_(program)));
};
$jscomp.initSymbol = function() {
};
$jscomp.polyfill("Symbol", function(orig) {
  if (orig) {
    return orig;
  }
  var SymbolClass = function(id, opt_description) {
    this.$jscomp$symbol$id_ = id;
    $jscomp.defineProperty(this, "description", {configurable:!0, writable:!0, value:opt_description});
  };
  SymbolClass.prototype.toString = function() {
    return this.$jscomp$symbol$id_;
  };
  var BIN_ID = 1E9 * Math.random() >>> 0, SYMBOL_PREFIX = "jscomp_symbol_" + BIN_ID + "_", counter = 0, symbolPolyfill = function(opt_description) {
    if (this instanceof symbolPolyfill) {
      throw new TypeError("Symbol is not a constructor");
    }
    return new SymbolClass(SYMBOL_PREFIX + (opt_description || "") + "_" + counter++, opt_description);
  };
  return symbolPolyfill;
}, "es6", "es3");
$jscomp.polyfill("Symbol.iterator", function(orig) {
  if (orig) {
    return orig;
  }
  for (var symbolIterator = Symbol("Symbol.iterator"), arrayLikes = "Array Int8Array Uint8Array Uint8ClampedArray Int16Array Uint16Array Int32Array Uint32Array Float32Array Float64Array".split(" "), i = 0; i < arrayLikes.length; i++) {
    var ArrayLikeCtor = $jscomp.global[arrayLikes[i]];
    "function" === typeof ArrayLikeCtor && "function" != typeof ArrayLikeCtor.prototype[symbolIterator] && $jscomp.defineProperty(ArrayLikeCtor.prototype, symbolIterator, {configurable:!0, writable:!0, value:function() {
      return $jscomp.iteratorPrototype($jscomp.arrayIteratorImpl(this));
    }});
  }
  return symbolIterator;
}, "es6", "es3");
$jscomp.iteratorPrototype = function(next) {
  var iterator = {next:next};
  iterator[Symbol.iterator] = function() {
    return this;
  };
  return iterator;
};
$jscomp.polyfill("Promise", function(NativePromise) {
  function AsyncExecutor() {
    this.batch_ = null;
  }
  function resolvingPromise(opt_value) {
    return opt_value instanceof PolyfillPromise ? opt_value : new PolyfillPromise(function(resolve) {
      resolve(opt_value);
    });
  }
  if (NativePromise && (!($jscomp.FORCE_POLYFILL_PROMISE || $jscomp.FORCE_POLYFILL_PROMISE_WHEN_NO_UNHANDLED_REJECTION && "undefined" === typeof $jscomp.global.PromiseRejectionEvent) || !$jscomp.global.Promise || -1 === $jscomp.global.Promise.toString().indexOf("[native code]"))) {
    return NativePromise;
  }
  AsyncExecutor.prototype.asyncExecute = function(f) {
    if (null == this.batch_) {
      this.batch_ = [];
      var self = this;
      this.asyncExecuteFunction(function() {
        self.executeBatch_();
      });
    }
    this.batch_.push(f);
  };
  var nativeSetTimeout = $jscomp.global.setTimeout;
  AsyncExecutor.prototype.asyncExecuteFunction = function(f) {
    nativeSetTimeout(f, 0);
  };
  AsyncExecutor.prototype.executeBatch_ = function() {
    for (; this.batch_ && this.batch_.length;) {
      var executingBatch = this.batch_;
      this.batch_ = [];
      for (var i = 0; i < executingBatch.length; ++i) {
        var f = executingBatch[i];
        executingBatch[i] = null;
        try {
          f();
        } catch (error) {
          this.asyncThrow_(error);
        }
      }
    }
    this.batch_ = null;
  };
  AsyncExecutor.prototype.asyncThrow_ = function(exception) {
    this.asyncExecuteFunction(function() {
      throw exception;
    });
  };
  var PromiseState = {PENDING:0, FULFILLED:1, REJECTED:2}, PolyfillPromise = function(executor) {
    this.state_ = PromiseState.PENDING;
    this.result_ = void 0;
    this.onSettledCallbacks_ = [];
    this.isRejectionHandled_ = !1;
    var resolveAndReject = this.createResolveAndReject_();
    try {
      executor(resolveAndReject.resolve, resolveAndReject.reject);
    } catch (e) {
      resolveAndReject.reject(e);
    }
  };
  PolyfillPromise.prototype.createResolveAndReject_ = function() {
    function firstCallWins(method) {
      return function(x) {
        alreadyCalled || (alreadyCalled = !0, method.call(thisPromise, x));
      };
    }
    var thisPromise = this, alreadyCalled = !1;
    return {resolve:firstCallWins(this.resolveTo_), reject:firstCallWins(this.reject_)};
  };
  PolyfillPromise.prototype.resolveTo_ = function(value) {
    if (value === this) {
      this.reject_(new TypeError("A Promise cannot resolve to itself"));
    } else if (value instanceof PolyfillPromise) {
      this.settleSameAsPromise_(value);
    } else {
      a: {
        switch(typeof value) {
          case "object":
            var JSCompiler_inline_result = null != value;
            break a;
          case "function":
            JSCompiler_inline_result = !0;
            break a;
          default:
            JSCompiler_inline_result = !1;
        }
      }
      JSCompiler_inline_result ? this.resolveToNonPromiseObj_(value) : this.fulfill_(value);
    }
  };
  PolyfillPromise.prototype.resolveToNonPromiseObj_ = function(obj) {
    var thenMethod = void 0;
    try {
      thenMethod = obj.then;
    } catch (error) {
      this.reject_(error);
      return;
    }
    "function" == typeof thenMethod ? this.settleSameAsThenable_(thenMethod, obj) : this.fulfill_(obj);
  };
  PolyfillPromise.prototype.reject_ = function(reason) {
    this.settle_(PromiseState.REJECTED, reason);
  };
  PolyfillPromise.prototype.fulfill_ = function(value) {
    this.settle_(PromiseState.FULFILLED, value);
  };
  PolyfillPromise.prototype.settle_ = function(settledState, valueOrReason) {
    if (this.state_ != PromiseState.PENDING) {
      throw Error("Cannot settle(" + settledState + ", " + valueOrReason + "): Promise already settled in state" + this.state_);
    }
    this.state_ = settledState;
    this.result_ = valueOrReason;
    this.state_ === PromiseState.REJECTED && this.scheduleUnhandledRejectionCheck_();
    this.executeOnSettledCallbacks_();
  };
  PolyfillPromise.prototype.scheduleUnhandledRejectionCheck_ = function() {
    var self = this;
    nativeSetTimeout(function() {
      if (self.notifyUnhandledRejection_()) {
        var nativeConsole = $jscomp.global.console;
        "undefined" !== typeof nativeConsole && nativeConsole.error(self.result_);
      }
    }, 1);
  };
  PolyfillPromise.prototype.notifyUnhandledRejection_ = function() {
    if (this.isRejectionHandled_) {
      return !1;
    }
    var NativeCustomEvent = $jscomp.global.CustomEvent, NativeEvent = $jscomp.global.Event, nativeDispatchEvent = $jscomp.global.dispatchEvent;
    if ("undefined" === typeof nativeDispatchEvent) {
      return !0;
    }
    if ("function" === typeof NativeCustomEvent) {
      var event = new NativeCustomEvent("unhandledrejection", {cancelable:!0});
    } else {
      "function" === typeof NativeEvent ? event = new NativeEvent("unhandledrejection", {cancelable:!0}) : (event = $jscomp.global.document.createEvent("CustomEvent"), event.initCustomEvent("unhandledrejection", !1, !0, event));
    }
    event.promise = this;
    event.reason = this.result_;
    return nativeDispatchEvent(event);
  };
  PolyfillPromise.prototype.executeOnSettledCallbacks_ = function() {
    if (null != this.onSettledCallbacks_) {
      for (var i = 0; i < this.onSettledCallbacks_.length; ++i) {
        asyncExecutor.asyncExecute(this.onSettledCallbacks_[i]);
      }
      this.onSettledCallbacks_ = null;
    }
  };
  var asyncExecutor = new AsyncExecutor();
  PolyfillPromise.prototype.settleSameAsPromise_ = function(promise) {
    var methods = this.createResolveAndReject_();
    promise.callWhenSettled_(methods.resolve, methods.reject);
  };
  PolyfillPromise.prototype.settleSameAsThenable_ = function(thenMethod, thenable) {
    var methods = this.createResolveAndReject_();
    try {
      thenMethod.call(thenable, methods.resolve, methods.reject);
    } catch (error) {
      methods.reject(error);
    }
  };
  PolyfillPromise.prototype.then = function(onFulfilled, onRejected) {
    function createCallback(paramF, defaultF) {
      return "function" == typeof paramF ? function(x) {
        try {
          resolveChild(paramF(x));
        } catch (error) {
          rejectChild(error);
        }
      } : defaultF;
    }
    var resolveChild, rejectChild, childPromise = new PolyfillPromise(function(resolve, reject) {
      resolveChild = resolve;
      rejectChild = reject;
    });
    this.callWhenSettled_(createCallback(onFulfilled, resolveChild), createCallback(onRejected, rejectChild));
    return childPromise;
  };
  PolyfillPromise.prototype.catch = function(onRejected) {
    return this.then(void 0, onRejected);
  };
  PolyfillPromise.prototype.callWhenSettled_ = function(onFulfilled, onRejected) {
    function callback() {
      switch(thisPromise.state_) {
        case PromiseState.FULFILLED:
          onFulfilled(thisPromise.result_);
          break;
        case PromiseState.REJECTED:
          onRejected(thisPromise.result_);
          break;
        default:
          throw Error("Unexpected state: " + thisPromise.state_);
      }
    }
    var thisPromise = this;
    null == this.onSettledCallbacks_ ? asyncExecutor.asyncExecute(callback) : this.onSettledCallbacks_.push(callback);
    this.isRejectionHandled_ = !0;
  };
  PolyfillPromise.resolve = resolvingPromise;
  PolyfillPromise.reject = function(opt_reason) {
    return new PolyfillPromise(function(resolve, reject) {
      reject(opt_reason);
    });
  };
  PolyfillPromise.race = function(thenablesOrValues) {
    return new PolyfillPromise(function(resolve, reject) {
      for (var iterator = $jscomp.makeIterator(thenablesOrValues), iterRec = iterator.next(); !iterRec.done; iterRec = iterator.next()) {
        resolvingPromise(iterRec.value).callWhenSettled_(resolve, reject);
      }
    });
  };
  PolyfillPromise.all = function(thenablesOrValues) {
    var iterator = $jscomp.makeIterator(thenablesOrValues), iterRec = iterator.next();
    return iterRec.done ? resolvingPromise([]) : new PolyfillPromise(function(resolveAll, rejectAll) {
      function onFulfilled(i) {
        return function(ithResult) {
          resultsArray[i] = ithResult;
          unresolvedCount--;
          0 == unresolvedCount && resolveAll(resultsArray);
        };
      }
      var resultsArray = [], unresolvedCount = 0;
      do {
        resultsArray.push(void 0), unresolvedCount++, resolvingPromise(iterRec.value).callWhenSettled_(onFulfilled(resultsArray.length - 1), rejectAll), iterRec = iterator.next();
      } while (!iterRec.done);
    });
  };
  return PolyfillPromise;
}, "es6", "es3");
$jscomp.checkEs6ConformanceViaProxy = function() {
  try {
    var proxied = {}, proxy = Object.create(new $jscomp.global.Proxy(proxied, {get:function(target, key, receiver) {
      return target == proxied && "q" == key && receiver == proxy;
    }}));
    return !0 === proxy.q;
  } catch (err) {
    return !1;
  }
};
$jscomp.USE_PROXY_FOR_ES6_CONFORMANCE_CHECKS = !1;
$jscomp.ES6_CONFORMANCE = $jscomp.USE_PROXY_FOR_ES6_CONFORMANCE_CHECKS && $jscomp.checkEs6ConformanceViaProxy();
$jscomp.owns = function(obj, prop) {
  return Object.prototype.hasOwnProperty.call(obj, prop);
};
$jscomp.polyfill("WeakMap", function(NativeWeakMap) {
  function isConformant() {
    if (!NativeWeakMap || !Object.seal) {
      return !1;
    }
    try {
      var x = Object.seal({}), y = Object.seal({}), map = new NativeWeakMap([[x, 2], [y, 3]]);
      if (2 != map.get(x) || 3 != map.get(y)) {
        return !1;
      }
      map.delete(x);
      map.set(y, 4);
      return !map.has(x) && 4 == map.get(y);
    } catch (err) {
      return !1;
    }
  }
  function WeakMapMembership() {
  }
  function isValidKey(key) {
    var type = typeof key;
    return "object" === type && null !== key || "function" === type;
  }
  function insert(target) {
    if (!$jscomp.owns(target, prop)) {
      var obj = new WeakMapMembership();
      $jscomp.defineProperty(target, prop, {value:obj});
    }
  }
  function patch(name) {
    if (!$jscomp.ISOLATE_POLYFILLS) {
      var prev = Object[name];
      prev && (Object[name] = function(target) {
        if (target instanceof WeakMapMembership) {
          return target;
        }
        Object.isExtensible(target) && insert(target);
        return prev(target);
      });
    }
  }
  if ($jscomp.USE_PROXY_FOR_ES6_CONFORMANCE_CHECKS) {
    if (NativeWeakMap && $jscomp.ES6_CONFORMANCE) {
      return NativeWeakMap;
    }
  } else {
    if (isConformant()) {
      return NativeWeakMap;
    }
  }
  var prop = "$jscomp_hidden_" + Math.random();
  patch("freeze");
  patch("preventExtensions");
  patch("seal");
  var index = 0, PolyfillWeakMap = function(opt_iterable) {
    this.id_ = (index += Math.random() + 1).toString();
    if (opt_iterable) {
      for (var iter = $jscomp.makeIterator(opt_iterable), entry; !(entry = iter.next()).done;) {
        var item = entry.value;
        this.set(item[0], item[1]);
      }
    }
  };
  PolyfillWeakMap.prototype.set = function(key, value) {
    if (!isValidKey(key)) {
      throw Error("Invalid WeakMap key");
    }
    insert(key);
    if (!$jscomp.owns(key, prop)) {
      throw Error("WeakMap key fail: " + key);
    }
    key[prop][this.id_] = value;
    return this;
  };
  PolyfillWeakMap.prototype.get = function(key) {
    return isValidKey(key) && $jscomp.owns(key, prop) ? key[prop][this.id_] : void 0;
  };
  PolyfillWeakMap.prototype.has = function(key) {
    return isValidKey(key) && $jscomp.owns(key, prop) && $jscomp.owns(key[prop], this.id_);
  };
  PolyfillWeakMap.prototype.delete = function(key) {
    return isValidKey(key) && $jscomp.owns(key, prop) && $jscomp.owns(key[prop], this.id_) ? delete key[prop][this.id_] : !1;
  };
  return PolyfillWeakMap;
}, "es6", "es3");
$jscomp.MapEntry = function() {
};
$jscomp.polyfill("Map", function(NativeMap) {
  function isConformant() {
    if ($jscomp.ASSUME_NO_NATIVE_MAP || !NativeMap || "function" != typeof NativeMap || !NativeMap.prototype.entries || "function" != typeof Object.seal) {
      return !1;
    }
    try {
      var key = Object.seal({x:4}), map = new NativeMap($jscomp.makeIterator([[key, "s"]]));
      if ("s" != map.get(key) || 1 != map.size || map.get({x:4}) || map.set({x:4}, "t") != map || 2 != map.size) {
        return !1;
      }
      var iter = map.entries(), item = iter.next();
      if (item.done || item.value[0] != key || "s" != item.value[1]) {
        return !1;
      }
      item = iter.next();
      return item.done || 4 != item.value[0].x || "t" != item.value[1] || !iter.next().done ? !1 : !0;
    } catch (err) {
      return !1;
    }
  }
  if ($jscomp.USE_PROXY_FOR_ES6_CONFORMANCE_CHECKS) {
    if (NativeMap && $jscomp.ES6_CONFORMANCE) {
      return NativeMap;
    }
  } else {
    if (isConformant()) {
      return NativeMap;
    }
  }
  var idMap = new WeakMap(), PolyfillMap = function(opt_iterable) {
    this.data_ = {};
    this.head_ = createHead();
    this.size = 0;
    if (opt_iterable) {
      for (var iter = $jscomp.makeIterator(opt_iterable), entry; !(entry = iter.next()).done;) {
        var item = entry.value;
        this.set(item[0], item[1]);
      }
    }
  };
  PolyfillMap.prototype.set = function(key, value) {
    key = 0 === key ? 0 : key;
    var r = maybeGetEntry(this, key);
    r.list || (r.list = this.data_[r.id] = []);
    r.entry ? r.entry.value = value : (r.entry = {next:this.head_, previous:this.head_.previous, head:this.head_, key:key, value:value,}, r.list.push(r.entry), this.head_.previous.next = r.entry, this.head_.previous = r.entry, this.size++);
    return this;
  };
  PolyfillMap.prototype.delete = function(key) {
    var r = maybeGetEntry(this, key);
    return r.entry && r.list ? (r.list.splice(r.index, 1), r.list.length || delete this.data_[r.id], r.entry.previous.next = r.entry.next, r.entry.next.previous = r.entry.previous, r.entry.head = null, this.size--, !0) : !1;
  };
  PolyfillMap.prototype.clear = function() {
    this.data_ = {};
    this.head_ = this.head_.previous = createHead();
    this.size = 0;
  };
  PolyfillMap.prototype.has = function(key) {
    return !!maybeGetEntry(this, key).entry;
  };
  PolyfillMap.prototype.get = function(key) {
    var entry = maybeGetEntry(this, key).entry;
    return entry && entry.value;
  };
  PolyfillMap.prototype.entries = function() {
    return makeIterator(this, function(entry) {
      return [entry.key, entry.value];
    });
  };
  PolyfillMap.prototype.keys = function() {
    return makeIterator(this, function(entry) {
      return entry.key;
    });
  };
  PolyfillMap.prototype.values = function() {
    return makeIterator(this, function(entry) {
      return entry.value;
    });
  };
  PolyfillMap.prototype.forEach = function(callback, opt_thisArg) {
    for (var iter = this.entries(), item; !(item = iter.next()).done;) {
      var entry = item.value;
      callback.call(opt_thisArg, entry[1], entry[0], this);
    }
  };
  PolyfillMap.prototype[Symbol.iterator] = PolyfillMap.prototype.entries;
  var maybeGetEntry = function(map, key) {
    var obj = key, type = obj && typeof obj;
    if ("object" == type || "function" == type) {
      if (idMap.has(obj)) {
        var id = idMap.get(obj);
      } else {
        var id$jscomp$0 = "" + ++mapIndex;
        idMap.set(obj, id$jscomp$0);
        id = id$jscomp$0;
      }
    } else {
      id = "p_" + obj;
    }
    var list = map.data_[id];
    if (list && $jscomp.owns(map.data_, id)) {
      for (var index = 0; index < list.length; index++) {
        var entry = list[index];
        if (key !== key && entry.key !== entry.key || key === entry.key) {
          return {id:id, list:list, index:index, entry:entry};
        }
      }
    }
    return {id:id, list:list, index:-1, entry:void 0};
  }, makeIterator = function(map, func) {
    var entry = map.head_;
    return $jscomp.iteratorPrototype(function() {
      if (entry) {
        for (; entry.head != map.head_;) {
          entry = entry.previous;
        }
        for (; entry.next != entry.head;) {
          return entry = entry.next, {done:!1, value:func(entry)};
        }
        entry = null;
      }
      return {done:!0, value:void 0};
    });
  }, createHead = function() {
    var head = {};
    return head.previous = head.next = head.head = head;
  }, mapIndex = 0;
  return PolyfillMap;
}, "es6", "es3");
$jscomp.findInternal = function(array, callback, thisArg) {
  array instanceof String && (array = String(array));
  for (var len = array.length, i = 0; i < len; i++) {
    var value = array[i];
    if (callback.call(thisArg, value, i, array)) {
      return {i:i, v:value};
    }
  }
  return {i:-1, v:void 0};
};
$jscomp.polyfill("Array.prototype.find", function(orig) {
  if (orig) {
    return orig;
  }
  var polyfill = function(callback, opt_thisArg) {
    return $jscomp.findInternal(this, callback, opt_thisArg).v;
  };
  return polyfill;
}, "es6", "es3");
$jscomp.checkStringArgs = function(thisArg, arg, func) {
  if (null == thisArg) {
    throw new TypeError("The 'this' value for String.prototype." + func + " must not be null or undefined");
  }
  if (arg instanceof RegExp) {
    throw new TypeError("First argument to String.prototype." + func + " must not be a regular expression");
  }
  return thisArg + "";
};
$jscomp.polyfill("String.prototype.endsWith", function(orig) {
  if (orig) {
    return orig;
  }
  var polyfill = function(searchString, opt_position) {
    var string = $jscomp.checkStringArgs(this, searchString, "endsWith");
    searchString += "";
    void 0 === opt_position && (opt_position = string.length);
    for (var i = Math.max(0, Math.min(opt_position | 0, string.length)), j = searchString.length; 0 < j && 0 < i;) {
      if (string[--i] != searchString[--j]) {
        return !1;
      }
    }
    return 0 >= j;
  };
  return polyfill;
}, "es6", "es3");
$jscomp.polyfill("String.prototype.startsWith", function(orig) {
  if (orig) {
    return orig;
  }
  var polyfill = function(searchString, opt_position) {
    var string = $jscomp.checkStringArgs(this, searchString, "startsWith");
    searchString += "";
    for (var strLen = string.length, searchLen = searchString.length, i = Math.max(0, Math.min(opt_position | 0, string.length)), j = 0; j < searchLen && i < strLen;) {
      if (string[i++] != searchString[j++]) {
        return !1;
      }
    }
    return j >= searchLen;
  };
  return polyfill;
}, "es6", "es3");
$jscomp.polyfill("Number.isFinite", function(orig) {
  if (orig) {
    return orig;
  }
  var polyfill = function(x) {
    return "number" !== typeof x ? !1 : !isNaN(x) && Infinity !== x && -Infinity !== x;
  };
  return polyfill;
}, "es6", "es3");
$jscomp.polyfill("String.prototype.repeat", function(orig) {
  if (orig) {
    return orig;
  }
  var polyfill = function(copies) {
    var string = $jscomp.checkStringArgs(this, null, "repeat");
    if (0 > copies || 1342177279 < copies) {
      throw new RangeError("Invalid count value");
    }
    copies |= 0;
    for (var result = ""; copies;) {
      if (copies & 1 && (result += string), copies >>>= 1) {
        string += string;
      }
    }
    return result;
  };
  return polyfill;
}, "es6", "es3");
$jscomp.polyfill("String.prototype.trimLeft", function(orig) {
  function polyfill() {
    return this.replace(/^[\s\xa0]+/, "");
  }
  return orig || polyfill;
}, "es_2019", "es3");
$jscomp.iteratorFromArray = function(array, transform) {
  array instanceof String && (array += "");
  var i = 0, done = !1, iter = {next:function() {
    if (!done && i < array.length) {
      var index = i++;
      return {value:transform(index, array[index]), done:!1};
    }
    done = !0;
    return {done:!0, value:void 0};
  }};
  iter[Symbol.iterator] = function() {
    return iter;
  };
  return iter;
};
$jscomp.polyfill("Array.prototype.values", function(orig) {
  if (orig) {
    return orig;
  }
  var polyfill = function() {
    return $jscomp.iteratorFromArray(this, function(k, v) {
      return v;
    });
  };
  return polyfill;
}, "es8", "es3");
$jscomp.polyfill("Array.prototype.keys", function(orig) {
  if (orig) {
    return orig;
  }
  var polyfill = function() {
    return $jscomp.iteratorFromArray(this, function(i) {
      return i;
    });
  };
  return polyfill;
}, "es6", "es3");
$jscomp.polyfill("Array.prototype.entries", function(orig) {
  if (orig) {
    return orig;
  }
  var polyfill = function() {
    return $jscomp.iteratorFromArray(this, function(i, v) {
      return [i, v];
    });
  };
  return polyfill;
}, "es6", "es3");
$jscomp.polyfill("Array.from", function(orig) {
  if (orig) {
    return orig;
  }
  var polyfill = function(arrayLike, opt_mapFn, opt_thisArg) {
    opt_mapFn = null != opt_mapFn ? opt_mapFn : function(x) {
      return x;
    };
    var result = [], iteratorFunction = "undefined" != typeof Symbol && Symbol.iterator && arrayLike[Symbol.iterator];
    if ("function" == typeof iteratorFunction) {
      arrayLike = iteratorFunction.call(arrayLike);
      for (var next, k = 0; !(next = arrayLike.next()).done;) {
        result.push(opt_mapFn.call(opt_thisArg, next.value, k++));
      }
    } else {
      for (var len = arrayLike.length, i = 0; i < len; i++) {
        result.push(opt_mapFn.call(opt_thisArg, arrayLike[i], i));
      }
    }
    return result;
  };
  return polyfill;
}, "es6", "es3");
var goog = goog || {};
goog.global = this || self;
goog.exportPath_ = function(name, object, overwriteImplicit, objectToExportTo) {
  var parts = name.split("."), cur = objectToExportTo || goog.global;
  parts[0] in cur || "undefined" == typeof cur.execScript || cur.execScript("var " + parts[0]);
  for (var part; parts.length && (part = parts.shift());) {
    if (parts.length || void 0 === object) {
      cur = cur[part] && cur[part] !== Object.prototype[part] ? cur[part] : cur[part] = {};
    } else {
      if (!overwriteImplicit && goog.isObject(object) && goog.isObject(cur[part])) {
        for (var prop in object) {
          object.hasOwnProperty(prop) && (cur[part][prop] = object[prop]);
        }
      } else {
        cur[part] = object;
      }
    }
  }
};
goog.define = function(name, defaultValue) {
  var value = defaultValue;
  return value;
};
goog.FEATURESET_YEAR = 2012;
goog.DEBUG = !0;
goog.LOCALE = "en";
goog.getLocale = function() {
  return "en";
};
goog.TRUSTED_SITE = !0;
goog.DISALLOW_TEST_ONLY_CODE = !goog.DEBUG;
goog.ENABLE_CHROME_APP_SAFE_SCRIPT_LOADING = !1;
goog.provide = function(name) {
  if (goog.isInModuleLoader_()) {
    throw Error("goog.provide cannot be used within a module.");
  }
  goog.constructNamespace_(name);
};
goog.constructNamespace_ = function(name, object, overwriteImplicit) {
  goog.exportPath_(name, object, overwriteImplicit);
};
goog.NONCE_PATTERN_ = /^[\w+/_-]+[=]{0,2}$/;
goog.getScriptNonce_ = function(opt_window) {
  var doc = (opt_window || goog.global).document, script = doc.querySelector && doc.querySelector("script[nonce]");
  if (script) {
    var nonce = script.nonce || script.getAttribute("nonce");
    if (nonce && goog.NONCE_PATTERN_.test(nonce)) {
      return nonce;
    }
  }
  return "";
};
goog.VALID_MODULE_RE_ = /^[a-zA-Z_$][a-zA-Z0-9._$]*$/;
goog.module = function(name) {
  if ("string" !== typeof name || !name || -1 == name.search(goog.VALID_MODULE_RE_)) {
    throw Error("Invalid module identifier");
  }
  if (!goog.isInGoogModuleLoader_()) {
    throw Error("Module " + name + " has been loaded incorrectly. Note, modules cannot be loaded as normal scripts. They require some kind of pre-processing step. You're likely trying to load a module via a script tag or as a part of a concatenated bundle without rewriting the module. For more info see: https://github.com/google/closure-library/wiki/goog.module:-an-ES6-module-like-alternative-to-goog.provide.");
  }
  if (goog.moduleLoaderState_.moduleName) {
    throw Error("goog.module may only be called once per module.");
  }
  goog.moduleLoaderState_.moduleName = name;
};
goog.module.get = function() {
  return null;
};
goog.module.getInternal_ = function() {
  return null;
};
goog.ModuleType = {ES6:"es6", GOOG:"goog"};
goog.moduleLoaderState_ = null;
goog.isInModuleLoader_ = function() {
  return goog.isInGoogModuleLoader_() || goog.isInEs6ModuleLoader_();
};
goog.isInGoogModuleLoader_ = function() {
  return !!goog.moduleLoaderState_ && goog.moduleLoaderState_.type == goog.ModuleType.GOOG;
};
goog.isInEs6ModuleLoader_ = function() {
  var inLoader = !!goog.moduleLoaderState_ && goog.moduleLoaderState_.type == goog.ModuleType.ES6;
  if (inLoader) {
    return !0;
  }
  var jscomp = goog.global.$jscomp;
  return jscomp ? "function" != typeof jscomp.getCurrentModulePath ? !1 : !!jscomp.getCurrentModulePath() : !1;
};
goog.module.declareLegacyNamespace = function() {
  goog.moduleLoaderState_.declareLegacyNamespace = !0;
};
goog.declareModuleId = function(namespace) {
  if (goog.moduleLoaderState_) {
    goog.moduleLoaderState_.moduleName = namespace;
  } else {
    var jscomp = goog.global.$jscomp;
    if (!jscomp || "function" != typeof jscomp.getCurrentModulePath) {
      throw Error('Module with namespace "' + namespace + '" has been loaded incorrectly.');
    }
    var exports = jscomp.require(jscomp.getCurrentModulePath());
    goog.loadedModules_[namespace] = {exports:exports, type:goog.ModuleType.ES6, moduleId:namespace};
  }
};
goog.setTestOnly = function(opt_message) {
  if (goog.DISALLOW_TEST_ONLY_CODE) {
    throw opt_message = opt_message || "", Error("Importing test-only code into non-debug environment" + (opt_message ? ": " + opt_message : "."));
  }
};
goog.forwardDeclare = function() {
};
goog.getObjectByName = function(name, opt_obj) {
  for (var parts = name.split("."), cur = opt_obj || goog.global, i = 0; i < parts.length; i++) {
    if (cur = cur[parts[i]], null == cur) {
      return null;
    }
  }
  return cur;
};
goog.addDependency = function() {
};
goog.ENABLE_DEBUG_LOADER = !0;
goog.logToConsole_ = function(msg) {
  goog.global.console && goog.global.console.error(msg);
};
goog.require = function() {
};
goog.requireType = function() {
  return {};
};
goog.basePath = "";
goog.abstractMethod = function() {
  throw Error("unimplemented abstract method");
};
goog.addSingletonGetter = function(ctor) {
  ctor.instance_ = void 0;
  ctor.getInstance = function() {
    if (ctor.instance_) {
      return ctor.instance_;
    }
    goog.DEBUG && (goog.instantiatedSingletons_[goog.instantiatedSingletons_.length] = ctor);
    return ctor.instance_ = new ctor();
  };
};
goog.instantiatedSingletons_ = [];
goog.LOAD_MODULE_USING_EVAL = !0;
goog.SEAL_MODULE_EXPORTS = goog.DEBUG;
goog.loadedModules_ = {};
goog.DEPENDENCIES_ENABLED = !1;
goog.TRANSPILE = "detect";
goog.ASSUME_ES_MODULES_TRANSPILED = !1;
goog.TRUSTED_TYPES_POLICY_NAME = "goog";
goog.hasBadLetScoping = null;
goog.loadModule = function(moduleDef) {
  var previousState = goog.moduleLoaderState_;
  try {
    goog.moduleLoaderState_ = {moduleName:"", declareLegacyNamespace:!1, type:goog.ModuleType.GOOG};
    var origExports = {}, exports = origExports;
    if ("function" === typeof moduleDef) {
      exports = moduleDef.call(void 0, exports);
    } else if ("string" === typeof moduleDef) {
      exports = goog.loadModuleFromSource_.call(void 0, exports, moduleDef);
    } else {
      throw Error("Invalid module definition");
    }
    var moduleName = goog.moduleLoaderState_.moduleName;
    if ("string" === typeof moduleName && moduleName) {
      if (goog.moduleLoaderState_.declareLegacyNamespace) {
        var isDefaultExport = origExports !== exports;
        goog.constructNamespace_(moduleName, exports, isDefaultExport);
      } else {
        goog.SEAL_MODULE_EXPORTS && Object.seal && "object" == typeof exports && null != exports && Object.seal(exports);
      }
      var data = {exports:exports, type:goog.ModuleType.GOOG, moduleId:goog.moduleLoaderState_.moduleName};
      goog.loadedModules_[moduleName] = data;
    } else {
      throw Error('Invalid module name "' + moduleName + '"');
    }
  } finally {
    goog.moduleLoaderState_ = previousState;
  }
};
goog.loadModuleFromSource_ = function(exports, JSCompiler_OptimizeArgumentsArray_p0) {
  eval(goog.CLOSURE_EVAL_PREFILTER_.createScript(JSCompiler_OptimizeArgumentsArray_p0));
  return exports;
};
goog.normalizePath_ = function(path) {
  for (var components = path.split("/"), i = 0; i < components.length;) {
    "." == components[i] ? components.splice(i, 1) : i && ".." == components[i] && components[i - 1] && ".." != components[i - 1] ? components.splice(--i, 2) : i++;
  }
  return components.join("/");
};
goog.loadFileSync_ = function(src) {
  if (goog.global.CLOSURE_LOAD_FILE_SYNC) {
    return goog.global.CLOSURE_LOAD_FILE_SYNC(src);
  }
  try {
    var xhr = new goog.global.XMLHttpRequest();
    xhr.open("get", src, !1);
    xhr.send();
    return 0 == xhr.status || 200 == xhr.status ? xhr.responseText : null;
  } catch (err) {
    return null;
  }
};
goog.typeOf = function(value) {
  var s = typeof value;
  return "object" != s ? s : value ? Array.isArray(value) ? "array" : s : "null";
};
goog.isArrayLike = function(val) {
  var type = goog.typeOf(val);
  return "array" == type || "object" == type && "number" == typeof val.length;
};
goog.isDateLike = function(val) {
  return goog.isObject(val) && "function" == typeof val.getFullYear;
};
goog.isObject = function(val) {
  var type = typeof val;
  return "object" == type && null != val || "function" == type;
};
goog.getUid = function(obj) {
  return Object.prototype.hasOwnProperty.call(obj, goog.UID_PROPERTY_) && obj[goog.UID_PROPERTY_] || (obj[goog.UID_PROPERTY_] = ++goog.uidCounter_);
};
goog.hasUid = function(obj) {
  return !!obj[goog.UID_PROPERTY_];
};
goog.removeUid = function(obj) {
  null !== obj && "removeAttribute" in obj && obj.removeAttribute(goog.UID_PROPERTY_);
  try {
    delete obj[goog.UID_PROPERTY_];
  } catch (ex) {
  }
};
goog.UID_PROPERTY_ = "closure_uid_" + (1E9 * Math.random() >>> 0);
goog.uidCounter_ = 0;
goog.cloneObject = function(obj) {
  var type = goog.typeOf(obj);
  if ("object" == type || "array" == type) {
    if ("function" === typeof obj.clone) {
      return obj.clone();
    }
    if ("undefined" !== typeof Map && obj instanceof Map) {
      return new Map(obj);
    }
    if ("undefined" !== typeof Set && obj instanceof Set) {
      return new Set(obj);
    }
    var clone = "array" == type ? [] : {}, key;
    for (key in obj) {
      clone[key] = goog.cloneObject(obj[key]);
    }
    return clone;
  }
  return obj;
};
goog.bindNative_ = function(fn, selfObj, var_args) {
  return fn.call.apply(fn.bind, arguments);
};
goog.bindJs_ = function(fn, selfObj, var_args) {
  if (!fn) {
    throw Error();
  }
  if (2 < arguments.length) {
    var boundArgs = Array.prototype.slice.call(arguments, 2);
    return function() {
      var newArgs = Array.prototype.slice.call(arguments);
      Array.prototype.unshift.apply(newArgs, boundArgs);
      return fn.apply(selfObj, newArgs);
    };
  }
  return function() {
    return fn.apply(selfObj, arguments);
  };
};
goog.bind = function(fn, selfObj, var_args) {
  Function.prototype.bind && -1 != Function.prototype.bind.toString().indexOf("native code") ? goog.bind = goog.bindNative_ : goog.bind = goog.bindJs_;
  return goog.bind.apply(null, arguments);
};
goog.partial = function(fn, var_args) {
  var args = Array.prototype.slice.call(arguments, 1);
  return function() {
    var newArgs = args.slice();
    newArgs.push.apply(newArgs, arguments);
    return fn.apply(this, newArgs);
  };
};
goog.now = function() {
  return Date.now();
};
goog.globalEval = function(script) {
  (0,eval)(script);
};
goog.getCssName = function(className, opt_modifier) {
  if ("." == String(className).charAt(0)) {
    throw Error('className passed in goog.getCssName must not start with ".". You passed: ' + className);
  }
  var getMapping = function(cssName) {
    return goog.cssNameMapping_[cssName] || cssName;
  }, renameByParts = function(cssName) {
    for (var parts = cssName.split("-"), mapped = [], i = 0; i < parts.length; i++) {
      mapped.push(getMapping(parts[i]));
    }
    return mapped.join("-");
  };
  var rename = goog.cssNameMapping_ ? "BY_WHOLE" == goog.cssNameMappingStyle_ ? getMapping : renameByParts : function(a) {
    return a;
  };
  var result = opt_modifier ? className + "-" + rename(opt_modifier) : rename(className);
  return goog.global.CLOSURE_CSS_NAME_MAP_FN ? goog.global.CLOSURE_CSS_NAME_MAP_FN(result) : result;
};
goog.setCssNameMapping = function(mapping, opt_style) {
  goog.cssNameMapping_ = mapping;
  goog.cssNameMappingStyle_ = opt_style;
};
goog.GetMsgOptions = function() {
};
goog.getMsg = function(str, opt_values, opt_options) {
  opt_options && opt_options.html && (str = str.replace(/</g, "&lt;"));
  opt_options && opt_options.unescapeHtmlEntities && (str = str.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&apos;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&"));
  opt_values && (str = str.replace(/\{\$([^}]+)}/g, function(match, key) {
    return null != opt_values && key in opt_values ? opt_values[key] : match;
  }));
  return str;
};
goog.getMsgWithFallback = function(a) {
  return a;
};
goog.exportSymbol = function(publicPath, object, objectToExportTo) {
  goog.exportPath_(publicPath, object, !0, objectToExportTo);
};
goog.exportProperty = function(object, publicName, symbol) {
  object[publicName] = symbol;
};
goog.inherits = function(childCtor, parentCtor) {
  function tempCtor() {
  }
  tempCtor.prototype = parentCtor.prototype;
  childCtor.superClass_ = parentCtor.prototype;
  childCtor.prototype = new tempCtor();
  childCtor.prototype.constructor = childCtor;
  childCtor.base = function(me, methodName, var_args) {
    for (var args = Array(arguments.length - 2), i = 2; i < arguments.length; i++) {
      args[i - 2] = arguments[i];
    }
    return parentCtor.prototype[methodName].apply(me, args);
  };
};
goog.scope = function(fn) {
  if (goog.isInModuleLoader_()) {
    throw Error("goog.scope is not supported within a module.");
  }
  fn.call(goog.global);
};
goog.defineClass = function(superClass, def) {
  var constructor = def.constructor, statics = def.statics;
  constructor && constructor != Object.prototype.constructor || (constructor = function() {
    throw Error("cannot instantiate an interface (no constructor defined).");
  });
  var cls = goog.defineClass.createSealingConstructor_(constructor, superClass);
  superClass && goog.inherits(cls, superClass);
  delete def.constructor;
  delete def.statics;
  goog.defineClass.applyProperties_(cls.prototype, def);
  null != statics && (statics instanceof Function ? statics(cls) : goog.defineClass.applyProperties_(cls, statics));
  return cls;
};
goog.defineClass.SEAL_CLASS_INSTANCES = goog.DEBUG;
goog.defineClass.createSealingConstructor_ = function(ctr) {
  if (!goog.defineClass.SEAL_CLASS_INSTANCES) {
    return ctr;
  }
  var wrappedCtr = function() {
    var instance = ctr.apply(this, arguments) || this;
    instance[goog.UID_PROPERTY_] = instance[goog.UID_PROPERTY_];
    return instance;
  };
  return wrappedCtr;
};
goog.defineClass.OBJECT_PROTOTYPE_FIELDS_ = "constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" ");
goog.defineClass.applyProperties_ = function(target, source) {
  for (var key in source) {
    Object.prototype.hasOwnProperty.call(source, key) && (target[key] = source[key]);
  }
  for (var i = 0; i < goog.defineClass.OBJECT_PROTOTYPE_FIELDS_.length; i++) {
    key = goog.defineClass.OBJECT_PROTOTYPE_FIELDS_[i], Object.prototype.hasOwnProperty.call(source, key) && (target[key] = source[key]);
  }
};
goog.identity_ = function(s) {
  return s;
};
goog.createTrustedTypesPolicy = function(name) {
  var policy = null, policyFactory = goog.global.trustedTypes;
  if (!policyFactory || !policyFactory.createPolicy) {
    return policy;
  }
  try {
    policy = policyFactory.createPolicy(name, {createHTML:goog.identity_, createScript:goog.identity_, createScriptURL:goog.identity_});
  } catch (e) {
    goog.logToConsole_(e.message);
  }
  return policy;
};
goog.debug = {};
function module$contents$goog$debug$Error_DebugError(msg, cause) {
  if (Error.captureStackTrace) {
    Error.captureStackTrace(this, module$contents$goog$debug$Error_DebugError);
  } else {
    var stack = Error().stack;
    stack && (this.stack = stack);
  }
  msg && (this.message = String(msg));
  void 0 !== cause && (this.cause = cause);
}
goog.inherits(module$contents$goog$debug$Error_DebugError, Error);
module$contents$goog$debug$Error_DebugError.prototype.name = "CustomError";
goog.debug.Error = module$contents$goog$debug$Error_DebugError;
goog.dom = {};
goog.dom.NodeType = {ELEMENT:1, ATTRIBUTE:2, TEXT:3, CDATA_SECTION:4, ENTITY_REFERENCE:5, ENTITY:6, PROCESSING_INSTRUCTION:7, COMMENT:8, DOCUMENT:9, DOCUMENT_TYPE:10, DOCUMENT_FRAGMENT:11, NOTATION:12};
goog.asserts = {};
goog.asserts.ENABLE_ASSERTS = goog.DEBUG;
function module$contents$goog$asserts_AssertionError(messagePattern, messageArgs) {
  for (var JSCompiler_temp_const = module$contents$goog$debug$Error_DebugError, JSCompiler_temp_const$jscomp$0 = JSCompiler_temp_const.call, JSCompiler_inline_result, subs = messageArgs, splitParts = messagePattern.split("%s"), returnString = "", subLast = splitParts.length - 1, i = 0; i < subLast; i++) {
    var sub = i < subs.length ? subs[i] : "%s";
    returnString += splitParts[i] + sub;
  }
  JSCompiler_inline_result = returnString + splitParts[subLast];
  JSCompiler_temp_const$jscomp$0.call(JSCompiler_temp_const, this, JSCompiler_inline_result);
}
goog.inherits(module$contents$goog$asserts_AssertionError, module$contents$goog$debug$Error_DebugError);
goog.asserts.AssertionError = module$contents$goog$asserts_AssertionError;
module$contents$goog$asserts_AssertionError.prototype.name = "AssertionError";
goog.asserts.DEFAULT_ERROR_HANDLER = function(e) {
  throw e;
};
var module$contents$goog$asserts_errorHandler_ = goog.asserts.DEFAULT_ERROR_HANDLER;
function module$contents$goog$asserts_doAssertFailure(defaultMessage, defaultArgs, givenMessage, givenArgs) {
  var message = "Assertion failed";
  if (givenMessage) {
    message += ": " + givenMessage;
    var args = givenArgs;
  } else {
    defaultMessage && (message += ": " + defaultMessage, args = defaultArgs);
  }
  var e = new module$contents$goog$asserts_AssertionError("" + message, args || []);
  module$contents$goog$asserts_errorHandler_(e);
}
goog.asserts.setErrorHandler = function(errorHandler) {
  goog.asserts.ENABLE_ASSERTS && (module$contents$goog$asserts_errorHandler_ = errorHandler);
};
goog.asserts.assert = function(condition, opt_message, var_args) {
  goog.asserts.ENABLE_ASSERTS && !condition && module$contents$goog$asserts_doAssertFailure("", null, opt_message, Array.prototype.slice.call(arguments, 2));
  return condition;
};
goog.asserts.assertExists = function(value, opt_message, var_args) {
  goog.asserts.ENABLE_ASSERTS && null == value && module$contents$goog$asserts_doAssertFailure("Expected to exist: %s.", [value], opt_message, Array.prototype.slice.call(arguments, 2));
  return value;
};
goog.asserts.fail = function(opt_message, var_args) {
  goog.asserts.ENABLE_ASSERTS && module$contents$goog$asserts_errorHandler_(new module$contents$goog$asserts_AssertionError("Failure" + (opt_message ? ": " + opt_message : ""), Array.prototype.slice.call(arguments, 1)));
};
goog.asserts.assertNumber = function(value, opt_message, var_args) {
  goog.asserts.ENABLE_ASSERTS && "number" !== typeof value && module$contents$goog$asserts_doAssertFailure("Expected number but got %s: %s.", [goog.typeOf(value), value], opt_message, Array.prototype.slice.call(arguments, 2));
  return value;
};
goog.asserts.assertString = function(value, opt_message, var_args) {
  goog.asserts.ENABLE_ASSERTS && "string" !== typeof value && module$contents$goog$asserts_doAssertFailure("Expected string but got %s: %s.", [goog.typeOf(value), value], opt_message, Array.prototype.slice.call(arguments, 2));
  return value;
};
goog.asserts.assertFunction = function(value, opt_message, var_args) {
  goog.asserts.ENABLE_ASSERTS && "function" !== typeof value && module$contents$goog$asserts_doAssertFailure("Expected function but got %s: %s.", [goog.typeOf(value), value], opt_message, Array.prototype.slice.call(arguments, 2));
  return value;
};
goog.asserts.assertObject = function(value, opt_message, var_args) {
  goog.asserts.ENABLE_ASSERTS && !goog.isObject(value) && module$contents$goog$asserts_doAssertFailure("Expected object but got %s: %s.", [goog.typeOf(value), value], opt_message, Array.prototype.slice.call(arguments, 2));
  return value;
};
goog.asserts.assertArray = function(value, opt_message, var_args) {
  goog.asserts.ENABLE_ASSERTS && !Array.isArray(value) && module$contents$goog$asserts_doAssertFailure("Expected array but got %s: %s.", [goog.typeOf(value), value], opt_message, Array.prototype.slice.call(arguments, 2));
  return value;
};
goog.asserts.assertBoolean = function(value, opt_message, var_args) {
  goog.asserts.ENABLE_ASSERTS && "boolean" !== typeof value && module$contents$goog$asserts_doAssertFailure("Expected boolean but got %s: %s.", [goog.typeOf(value), value], opt_message, Array.prototype.slice.call(arguments, 2));
  return value;
};
goog.asserts.assertElement = function(value, opt_message, var_args) {
  !goog.asserts.ENABLE_ASSERTS || goog.isObject(value) && value.nodeType == goog.dom.NodeType.ELEMENT || module$contents$goog$asserts_doAssertFailure("Expected Element but got %s: %s.", [goog.typeOf(value), value], opt_message, Array.prototype.slice.call(arguments, 2));
  return value;
};
goog.asserts.assertInstanceof = function(value, type, opt_message, var_args) {
  !goog.asserts.ENABLE_ASSERTS || value instanceof type || module$contents$goog$asserts_doAssertFailure("Expected instanceof %s but got %s.", [module$contents$goog$asserts_getType(type), module$contents$goog$asserts_getType(value)], opt_message, Array.prototype.slice.call(arguments, 3));
  return value;
};
goog.asserts.assertFinite = function(value, opt_message, var_args) {
  !goog.asserts.ENABLE_ASSERTS || "number" == typeof value && isFinite(value) || module$contents$goog$asserts_doAssertFailure("Expected %s to be a finite number but it is not.", [value], opt_message, Array.prototype.slice.call(arguments, 2));
  return value;
};
function module$contents$goog$asserts_getType(value) {
  return value instanceof Function ? value.displayName || value.name || "unknown type name" : value instanceof Object ? value.constructor.displayName || value.constructor.name || Object.prototype.toString.call(value) : null === value ? "null" : typeof value;
}
;goog.array = {};
goog.NATIVE_ARRAY_PROTOTYPES = goog.TRUSTED_SITE;
var module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS = 2012 < goog.FEATURESET_YEAR;
goog.array.ASSUME_NATIVE_FUNCTIONS = module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS;
function module$contents$goog$array_peek(array) {
  return array[array.length - 1];
}
goog.array.peek = module$contents$goog$array_peek;
goog.array.last = module$contents$goog$array_peek;
var module$contents$goog$array_indexOf = goog.NATIVE_ARRAY_PROTOTYPES && (module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS || Array.prototype.indexOf) ? function(arr, obj, opt_fromIndex) {
  goog.asserts.assert(null != arr.length);
  return Array.prototype.indexOf.call(arr, obj, opt_fromIndex);
} : function(arr, obj, opt_fromIndex) {
  var fromIndex = null == opt_fromIndex ? 0 : 0 > opt_fromIndex ? Math.max(0, arr.length + opt_fromIndex) : opt_fromIndex;
  if ("string" === typeof arr) {
    return "string" !== typeof obj || 1 != obj.length ? -1 : arr.indexOf(obj, fromIndex);
  }
  for (var i = fromIndex; i < arr.length; i++) {
    if (i in arr && arr[i] === obj) {
      return i;
    }
  }
  return -1;
};
goog.array.indexOf = module$contents$goog$array_indexOf;
var module$contents$goog$array_lastIndexOf = goog.NATIVE_ARRAY_PROTOTYPES && (module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS || Array.prototype.lastIndexOf) ? function(arr, obj, opt_fromIndex) {
  goog.asserts.assert(null != arr.length);
  var fromIndex = null == opt_fromIndex ? arr.length - 1 : opt_fromIndex;
  return Array.prototype.lastIndexOf.call(arr, obj, fromIndex);
} : function(arr, obj, opt_fromIndex) {
  var fromIndex = null == opt_fromIndex ? arr.length - 1 : opt_fromIndex;
  0 > fromIndex && (fromIndex = Math.max(0, arr.length + fromIndex));
  if ("string" === typeof arr) {
    return "string" !== typeof obj || 1 != obj.length ? -1 : arr.lastIndexOf(obj, fromIndex);
  }
  for (var i = fromIndex; 0 <= i; i--) {
    if (i in arr && arr[i] === obj) {
      return i;
    }
  }
  return -1;
};
goog.array.lastIndexOf = module$contents$goog$array_lastIndexOf;
var module$contents$goog$array_forEach = goog.NATIVE_ARRAY_PROTOTYPES && (module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS || Array.prototype.forEach) ? function(arr, f, opt_obj) {
  goog.asserts.assert(null != arr.length);
  Array.prototype.forEach.call(arr, f, opt_obj);
} : function(arr, f, opt_obj) {
  for (var l = arr.length, arr2 = "string" === typeof arr ? arr.split("") : arr, i = 0; i < l; i++) {
    i in arr2 && f.call(opt_obj, arr2[i], i, arr);
  }
};
goog.array.forEach = module$contents$goog$array_forEach;
function module$contents$goog$array_forEachRight(arr, f, opt_obj) {
  for (var l = arr.length, arr2 = "string" === typeof arr ? arr.split("") : arr, i = l - 1; 0 <= i; --i) {
    i in arr2 && f.call(opt_obj, arr2[i], i, arr);
  }
}
goog.array.forEachRight = module$contents$goog$array_forEachRight;
var module$contents$goog$array_filter = goog.NATIVE_ARRAY_PROTOTYPES && (module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS || Array.prototype.filter) ? function(arr, f, opt_obj) {
  goog.asserts.assert(null != arr.length);
  return Array.prototype.filter.call(arr, f, opt_obj);
} : function(arr, f, opt_obj) {
  for (var l = arr.length, res = [], resLength = 0, arr2 = "string" === typeof arr ? arr.split("") : arr, i = 0; i < l; i++) {
    if (i in arr2) {
      var val = arr2[i];
      f.call(opt_obj, val, i, arr) && (res[resLength++] = val);
    }
  }
  return res;
};
goog.array.filter = module$contents$goog$array_filter;
var module$contents$goog$array_map = goog.NATIVE_ARRAY_PROTOTYPES && (module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS || Array.prototype.map) ? function(arr, f, opt_obj) {
  goog.asserts.assert(null != arr.length);
  return Array.prototype.map.call(arr, f, opt_obj);
} : function(arr, f, opt_obj) {
  for (var l = arr.length, res = Array(l), arr2 = "string" === typeof arr ? arr.split("") : arr, i = 0; i < l; i++) {
    i in arr2 && (res[i] = f.call(opt_obj, arr2[i], i, arr));
  }
  return res;
};
goog.array.map = module$contents$goog$array_map;
var module$contents$goog$array_reduce = goog.NATIVE_ARRAY_PROTOTYPES && (module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS || Array.prototype.reduce) ? function(arr, f, val, opt_obj) {
  goog.asserts.assert(null != arr.length);
  opt_obj && (f = goog.bind(f, opt_obj));
  return Array.prototype.reduce.call(arr, f, val);
} : function(arr, f, val$jscomp$0, opt_obj) {
  var rval = val$jscomp$0;
  module$contents$goog$array_forEach(arr, function(val, index) {
    rval = f.call(opt_obj, rval, val, index, arr);
  });
  return rval;
};
goog.array.reduce = module$contents$goog$array_reduce;
var module$contents$goog$array_reduceRight = goog.NATIVE_ARRAY_PROTOTYPES && (module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS || Array.prototype.reduceRight) ? function(arr, f, val, opt_obj) {
  goog.asserts.assert(null != arr.length);
  goog.asserts.assert(null != f);
  opt_obj && (f = goog.bind(f, opt_obj));
  return Array.prototype.reduceRight.call(arr, f, val);
} : function(arr, f, val$jscomp$0, opt_obj) {
  var rval = val$jscomp$0;
  module$contents$goog$array_forEachRight(arr, function(val, index) {
    rval = f.call(opt_obj, rval, val, index, arr);
  });
  return rval;
};
goog.array.reduceRight = module$contents$goog$array_reduceRight;
var module$contents$goog$array_some = goog.NATIVE_ARRAY_PROTOTYPES && (module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS || Array.prototype.some) ? function(arr, f, opt_obj) {
  goog.asserts.assert(null != arr.length);
  return Array.prototype.some.call(arr, f, opt_obj);
} : function(arr, f, opt_obj) {
  for (var l = arr.length, arr2 = "string" === typeof arr ? arr.split("") : arr, i = 0; i < l; i++) {
    if (i in arr2 && f.call(opt_obj, arr2[i], i, arr)) {
      return !0;
    }
  }
  return !1;
};
goog.array.some = module$contents$goog$array_some;
var module$contents$goog$array_every = goog.NATIVE_ARRAY_PROTOTYPES && (module$contents$goog$array_ASSUME_NATIVE_FUNCTIONS || Array.prototype.every) ? function(arr, f, opt_obj) {
  goog.asserts.assert(null != arr.length);
  return Array.prototype.every.call(arr, f, opt_obj);
} : function(arr, f, opt_obj) {
  for (var l = arr.length, arr2 = "string" === typeof arr ? arr.split("") : arr, i = 0; i < l; i++) {
    if (i in arr2 && !f.call(opt_obj, arr2[i], i, arr)) {
      return !1;
    }
  }
  return !0;
};
goog.array.every = module$contents$goog$array_every;
function module$contents$goog$array_count(arr$jscomp$0, f, opt_obj) {
  var count = 0;
  module$contents$goog$array_forEach(arr$jscomp$0, function(element, index, arr) {
    f.call(opt_obj, element, index, arr) && ++count;
  }, opt_obj);
  return count;
}
goog.array.count = module$contents$goog$array_count;
function module$contents$goog$array_find(arr, f, opt_obj) {
  var i = module$contents$goog$array_findIndex(arr, f, opt_obj);
  return 0 > i ? null : "string" === typeof arr ? arr.charAt(i) : arr[i];
}
goog.array.find = module$contents$goog$array_find;
function module$contents$goog$array_findIndex(arr, f, opt_obj) {
  for (var l = arr.length, arr2 = "string" === typeof arr ? arr.split("") : arr, i = 0; i < l; i++) {
    if (i in arr2 && f.call(opt_obj, arr2[i], i, arr)) {
      return i;
    }
  }
  return -1;
}
goog.array.findIndex = module$contents$goog$array_findIndex;
function module$contents$goog$array_findRight(arr, f, opt_obj) {
  var i = module$contents$goog$array_findIndexRight(arr, f, opt_obj);
  return 0 > i ? null : "string" === typeof arr ? arr.charAt(i) : arr[i];
}
goog.array.findRight = module$contents$goog$array_findRight;
function module$contents$goog$array_findIndexRight(arr, f, opt_obj) {
  for (var l = arr.length, arr2 = "string" === typeof arr ? arr.split("") : arr, i = l - 1; 0 <= i; i--) {
    if (i in arr2 && f.call(opt_obj, arr2[i], i, arr)) {
      return i;
    }
  }
  return -1;
}
goog.array.findIndexRight = module$contents$goog$array_findIndexRight;
function module$contents$goog$array_contains(arr, obj) {
  return 0 <= module$contents$goog$array_indexOf(arr, obj);
}
goog.array.contains = module$contents$goog$array_contains;
function module$contents$goog$array_isEmpty(arr) {
  return 0 == arr.length;
}
goog.array.isEmpty = module$contents$goog$array_isEmpty;
function module$contents$goog$array_clear(arr) {
  if (!Array.isArray(arr)) {
    for (var i = arr.length - 1; 0 <= i; i--) {
      delete arr[i];
    }
  }
  arr.length = 0;
}
goog.array.clear = module$contents$goog$array_clear;
function module$contents$goog$array_insert(arr, obj) {
  module$contents$goog$array_contains(arr, obj) || arr.push(obj);
}
goog.array.insert = module$contents$goog$array_insert;
function module$contents$goog$array_insertAt(arr, obj, opt_i) {
  module$contents$goog$array_splice(arr, opt_i, 0, obj);
}
goog.array.insertAt = module$contents$goog$array_insertAt;
function module$contents$goog$array_insertArrayAt(arr, elementsToAdd, opt_i) {
  goog.partial(module$contents$goog$array_splice, arr, opt_i, 0).apply(null, elementsToAdd);
}
goog.array.insertArrayAt = module$contents$goog$array_insertArrayAt;
function module$contents$goog$array_insertBefore(arr, obj, opt_obj2) {
  var i;
  2 == arguments.length || 0 > (i = module$contents$goog$array_indexOf(arr, opt_obj2)) ? arr.push(obj) : module$contents$goog$array_insertAt(arr, obj, i);
}
goog.array.insertBefore = module$contents$goog$array_insertBefore;
function module$contents$goog$array_remove(arr, obj) {
  var i = module$contents$goog$array_indexOf(arr, obj), rv;
  (rv = 0 <= i) && module$contents$goog$array_removeAt(arr, i);
  return rv;
}
goog.array.remove = module$contents$goog$array_remove;
function module$contents$goog$array_removeLast(arr, obj) {
  var i = module$contents$goog$array_lastIndexOf(arr, obj);
  return 0 <= i ? (module$contents$goog$array_removeAt(arr, i), !0) : !1;
}
goog.array.removeLast = module$contents$goog$array_removeLast;
function module$contents$goog$array_removeAt(arr, i) {
  goog.asserts.assert(null != arr.length);
  return 1 == Array.prototype.splice.call(arr, i, 1).length;
}
goog.array.removeAt = module$contents$goog$array_removeAt;
function module$contents$goog$array_removeIf(arr, f, opt_obj) {
  var i = module$contents$goog$array_findIndex(arr, f, opt_obj);
  return 0 <= i ? (module$contents$goog$array_removeAt(arr, i), !0) : !1;
}
goog.array.removeIf = module$contents$goog$array_removeIf;
function module$contents$goog$array_removeAllIf(arr, f, opt_obj) {
  var removedCount = 0;
  module$contents$goog$array_forEachRight(arr, function(val, index) {
    f.call(opt_obj, val, index, arr) && module$contents$goog$array_removeAt(arr, index) && removedCount++;
  });
  return removedCount;
}
goog.array.removeAllIf = module$contents$goog$array_removeAllIf;
function module$contents$goog$array_concat(var_args) {
  return Array.prototype.concat.apply([], arguments);
}
goog.array.concat = module$contents$goog$array_concat;
function module$contents$goog$array_join(var_args) {
  return Array.prototype.concat.apply([], arguments);
}
goog.array.join = module$contents$goog$array_join;
function module$contents$goog$array_toArray(object) {
  var length = object.length;
  if (0 < length) {
    for (var rv = Array(length), i = 0; i < length; i++) {
      rv[i] = object[i];
    }
    return rv;
  }
  return [];
}
goog.array.toArray = module$contents$goog$array_toArray;
goog.array.clone = module$contents$goog$array_toArray;
function module$contents$goog$array_extend(arr1, var_args) {
  for (var i = 1; i < arguments.length; i++) {
    var arr2 = arguments[i];
    if (goog.isArrayLike(arr2)) {
      var len1 = arr1.length || 0, len2 = arr2.length || 0;
      arr1.length = len1 + len2;
      for (var j = 0; j < len2; j++) {
        arr1[len1 + j] = arr2[j];
      }
    } else {
      arr1.push(arr2);
    }
  }
}
goog.array.extend = module$contents$goog$array_extend;
function module$contents$goog$array_splice(arr, index, howMany, var_args) {
  goog.asserts.assert(null != arr.length);
  return Array.prototype.splice.apply(arr, module$contents$goog$array_slice(arguments, 1));
}
goog.array.splice = module$contents$goog$array_splice;
function module$contents$goog$array_slice(arr, start, opt_end) {
  goog.asserts.assert(null != arr.length);
  return 2 >= arguments.length ? Array.prototype.slice.call(arr, start) : Array.prototype.slice.call(arr, start, opt_end);
}
goog.array.slice = module$contents$goog$array_slice;
function module$contents$goog$array_removeDuplicates(arr, opt_rv, opt_hashFn) {
  for (var returnArray = opt_rv || arr, defaultHashFn = function(item) {
    return goog.isObject(item) ? "o" + goog.getUid(item) : (typeof item).charAt(0) + item;
  }, hashFn = opt_hashFn || defaultHashFn, cursorInsert = 0, cursorRead = 0, seen = {}; cursorRead < arr.length;) {
    var current = arr[cursorRead++], key = hashFn(current);
    Object.prototype.hasOwnProperty.call(seen, key) || (seen[key] = !0, returnArray[cursorInsert++] = current);
  }
  returnArray.length = cursorInsert;
}
goog.array.removeDuplicates = module$contents$goog$array_removeDuplicates;
function module$contents$goog$array_binarySearch(arr, target, opt_compareFn) {
  return module$contents$goog$array_binarySearch_(arr, opt_compareFn || module$contents$goog$array_defaultCompare, !1, target);
}
goog.array.binarySearch = module$contents$goog$array_binarySearch;
function module$contents$goog$array_binarySelect(arr, evaluator, opt_obj) {
  return module$contents$goog$array_binarySearch_(arr, evaluator, !0, void 0, opt_obj);
}
goog.array.binarySelect = module$contents$goog$array_binarySelect;
function module$contents$goog$array_binarySearch_(arr, compareFn, isEvaluator, opt_target, opt_selfObj) {
  for (var left = 0, right = arr.length, found; left < right;) {
    var middle = left + (right - left >>> 1);
    var compareResult = isEvaluator ? compareFn.call(opt_selfObj, arr[middle], middle, arr) : compareFn(opt_target, arr[middle]);
    0 < compareResult ? left = middle + 1 : (right = middle, found = !compareResult);
  }
  return found ? left : -left - 1;
}
function module$contents$goog$array_sort(arr, opt_compareFn) {
  arr.sort(opt_compareFn || module$contents$goog$array_defaultCompare);
}
goog.array.sort = module$contents$goog$array_sort;
function module$contents$goog$array_stableSort(arr, opt_compareFn) {
  function stableCompareFn(obj1, obj2) {
    return valueCompareFn(obj1.value, obj2.value) || obj1.index - obj2.index;
  }
  for (var compArr = Array(arr.length), i = 0; i < arr.length; i++) {
    compArr[i] = {index:i, value:arr[i]};
  }
  var valueCompareFn = opt_compareFn || module$contents$goog$array_defaultCompare;
  module$contents$goog$array_sort(compArr, stableCompareFn);
  for (var i$7 = 0; i$7 < arr.length; i$7++) {
    arr[i$7] = compArr[i$7].value;
  }
}
goog.array.stableSort = module$contents$goog$array_stableSort;
function module$contents$goog$array_sortByKey(arr, keyFn, opt_compareFn) {
  var keyCompareFn = opt_compareFn || module$contents$goog$array_defaultCompare;
  module$contents$goog$array_sort(arr, function(a, b) {
    return keyCompareFn(keyFn(a), keyFn(b));
  });
}
goog.array.sortByKey = module$contents$goog$array_sortByKey;
function module$contents$goog$array_sortObjectsByKey(arr, key, opt_compareFn) {
  module$contents$goog$array_sortByKey(arr, function(obj) {
    return obj[key];
  }, opt_compareFn);
}
goog.array.sortObjectsByKey = module$contents$goog$array_sortObjectsByKey;
function module$contents$goog$array_isSorted(arr, opt_compareFn, opt_strict) {
  for (var compare = opt_compareFn || module$contents$goog$array_defaultCompare, i = 1; i < arr.length; i++) {
    var compareResult = compare(arr[i - 1], arr[i]);
    if (0 < compareResult || 0 == compareResult && opt_strict) {
      return !1;
    }
  }
  return !0;
}
goog.array.isSorted = module$contents$goog$array_isSorted;
function module$contents$goog$array_equals(arr1, arr2, opt_equalsFn) {
  if (!goog.isArrayLike(arr1) || !goog.isArrayLike(arr2) || arr1.length != arr2.length) {
    return !1;
  }
  for (var l = arr1.length, equalsFn = opt_equalsFn || module$contents$goog$array_defaultCompareEquality, i = 0; i < l; i++) {
    if (!equalsFn(arr1[i], arr2[i])) {
      return !1;
    }
  }
  return !0;
}
goog.array.equals = module$contents$goog$array_equals;
function module$contents$goog$array_compare3(arr1, arr2, opt_compareFn) {
  for (var compare = opt_compareFn || module$contents$goog$array_defaultCompare, l = Math.min(arr1.length, arr2.length), i = 0; i < l; i++) {
    var result = compare(arr1[i], arr2[i]);
    if (0 != result) {
      return result;
    }
  }
  return module$contents$goog$array_defaultCompare(arr1.length, arr2.length);
}
goog.array.compare3 = module$contents$goog$array_compare3;
function module$contents$goog$array_defaultCompare(a, b) {
  return a > b ? 1 : a < b ? -1 : 0;
}
goog.array.defaultCompare = module$contents$goog$array_defaultCompare;
function module$contents$goog$array_inverseDefaultCompare(a, b) {
  return -module$contents$goog$array_defaultCompare(a, b);
}
goog.array.inverseDefaultCompare = module$contents$goog$array_inverseDefaultCompare;
function module$contents$goog$array_defaultCompareEquality(a, b) {
  return a === b;
}
goog.array.defaultCompareEquality = module$contents$goog$array_defaultCompareEquality;
function module$contents$goog$array_binaryInsert(array, value, opt_compareFn) {
  var index = module$contents$goog$array_binarySearch(array, value, opt_compareFn);
  return 0 > index ? (module$contents$goog$array_insertAt(array, value, -(index + 1)), !0) : !1;
}
goog.array.binaryInsert = module$contents$goog$array_binaryInsert;
function module$contents$goog$array_binaryRemove(array, value, opt_compareFn) {
  var index = module$contents$goog$array_binarySearch(array, value, opt_compareFn);
  return 0 <= index ? module$contents$goog$array_removeAt(array, index) : !1;
}
goog.array.binaryRemove = module$contents$goog$array_binaryRemove;
function module$contents$goog$array_bucket(array, sorter, opt_obj) {
  for (var buckets = {}, i = 0; i < array.length; i++) {
    var value = array[i], key = sorter.call(opt_obj, value, i, array);
    if (void 0 !== key) {
      var bucket = buckets[key] || (buckets[key] = []);
      bucket.push(value);
    }
  }
  return buckets;
}
goog.array.bucket = module$contents$goog$array_bucket;
function module$contents$goog$array_bucketToMap(array, sorter) {
  for (var buckets = new Map(), i = 0; i < array.length; i++) {
    var value = array[i], key = sorter(value, i, array);
    if (void 0 !== key) {
      var bucket = buckets.get(key);
      bucket || (bucket = [], buckets.set(key, bucket));
      bucket.push(value);
    }
  }
  return buckets;
}
goog.array.bucketToMap = module$contents$goog$array_bucketToMap;
function module$contents$goog$array_toObject(arr, keyFunc, opt_obj) {
  var ret = {};
  module$contents$goog$array_forEach(arr, function(element, index) {
    ret[keyFunc.call(opt_obj, element, index, arr)] = element;
  });
  return ret;
}
goog.array.toObject = module$contents$goog$array_toObject;
function module$contents$goog$array_toMap(arr, keyFunc) {
  for (var map = new Map(), i = 0; i < arr.length; i++) {
    var element = arr[i];
    map.set(keyFunc(element, i, arr), element);
  }
  return map;
}
goog.array.toMap = module$contents$goog$array_toMap;
function module$contents$goog$array_range(startOrEnd, opt_end, opt_step) {
  var array = [], start = 0, end = startOrEnd, step = opt_step || 1;
  void 0 !== opt_end && (start = startOrEnd, end = opt_end);
  if (0 > step * (end - start)) {
    return [];
  }
  if (0 < step) {
    for (var i = start; i < end; i += step) {
      array.push(i);
    }
  } else {
    for (var i$8 = start; i$8 > end; i$8 += step) {
      array.push(i$8);
    }
  }
  return array;
}
goog.array.range = module$contents$goog$array_range;
function module$contents$goog$array_repeat(value, n) {
  for (var array = [], i = 0; i < n; i++) {
    array[i] = value;
  }
  return array;
}
goog.array.repeat = module$contents$goog$array_repeat;
function module$contents$goog$array_flatten(var_args) {
  for (var result = [], i = 0; i < arguments.length; i++) {
    var element = arguments[i];
    if (Array.isArray(element)) {
      for (var c = 0; c < element.length; c += 8192) {
        for (var chunk = module$contents$goog$array_slice(element, c, c + 8192), recurseResult = module$contents$goog$array_flatten.apply(null, chunk), r = 0; r < recurseResult.length; r++) {
          result.push(recurseResult[r]);
        }
      }
    } else {
      result.push(element);
    }
  }
  return result;
}
goog.array.flatten = module$contents$goog$array_flatten;
function module$contents$goog$array_rotate(array, n) {
  goog.asserts.assert(null != array.length);
  array.length && (n %= array.length, 0 < n ? Array.prototype.unshift.apply(array, array.splice(-n, n)) : 0 > n && Array.prototype.push.apply(array, array.splice(0, -n)));
  return array;
}
goog.array.rotate = module$contents$goog$array_rotate;
function module$contents$goog$array_moveItem(arr, fromIndex, toIndex) {
  goog.asserts.assert(0 <= fromIndex && fromIndex < arr.length);
  goog.asserts.assert(0 <= toIndex && toIndex < arr.length);
  var removedItems = Array.prototype.splice.call(arr, fromIndex, 1);
  Array.prototype.splice.call(arr, toIndex, 0, removedItems[0]);
}
goog.array.moveItem = module$contents$goog$array_moveItem;
function module$contents$goog$array_zip(var_args) {
  if (!arguments.length) {
    return [];
  }
  for (var result = [], minLen = arguments[0].length, i = 1; i < arguments.length; i++) {
    arguments[i].length < minLen && (minLen = arguments[i].length);
  }
  for (var i$9 = 0; i$9 < minLen; i$9++) {
    for (var value = [], j = 0; j < arguments.length; j++) {
      value.push(arguments[j][i$9]);
    }
    result.push(value);
  }
  return result;
}
goog.array.zip = module$contents$goog$array_zip;
function module$contents$goog$array_shuffle(arr, opt_randFn) {
  for (var randFn = opt_randFn || Math.random, i = arr.length - 1; 0 < i; i--) {
    var j = Math.floor(randFn() * (i + 1)), tmp = arr[i];
    arr[i] = arr[j];
    arr[j] = tmp;
  }
}
goog.array.shuffle = module$contents$goog$array_shuffle;
function module$contents$goog$array_copyByIndex(arr, index_arr) {
  var result = [];
  module$contents$goog$array_forEach(index_arr, function(index) {
    result.push(arr[index]);
  });
  return result;
}
goog.array.copyByIndex = module$contents$goog$array_copyByIndex;
function module$contents$goog$array_concatMap(arr, f, opt_obj) {
  return module$contents$goog$array_concat.apply([], module$contents$goog$array_map(arr, f, opt_obj));
}
goog.array.concatMap = module$contents$goog$array_concatMap;
goog.dom.asserts = {};
goog.dom.asserts.assertIsLocation = function(o) {
  if (goog.asserts.ENABLE_ASSERTS) {
    var win = goog.dom.asserts.getWindow_(o);
    win && (!o || !(o instanceof win.Location) && o instanceof win.Element) && goog.asserts.fail("Argument is not a Location (or a non-Element mock); got: %s", goog.dom.asserts.debugStringForType_(o));
  }
  return o;
};
goog.dom.asserts.assertIsElementType_ = function(o, typename) {
  if (goog.asserts.ENABLE_ASSERTS) {
    var win = goog.dom.asserts.getWindow_(o);
    win && "undefined" != typeof win[typename] && (o && (o instanceof win[typename] || !(o instanceof win.Location || o instanceof win.Element)) || goog.asserts.fail("Argument is not a %s (or a non-Element, non-Location mock); got: %s", typename, goog.dom.asserts.debugStringForType_(o)));
  }
  return o;
};
goog.dom.asserts.assertIsHTMLAnchorElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLAnchorElement");
};
goog.dom.asserts.assertIsHTMLButtonElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLButtonElement");
};
goog.dom.asserts.assertIsHTMLLinkElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLLinkElement");
};
goog.dom.asserts.assertIsHTMLImageElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLImageElement");
};
goog.dom.asserts.assertIsHTMLAudioElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLAudioElement");
};
goog.dom.asserts.assertIsHTMLVideoElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLVideoElement");
};
goog.dom.asserts.assertIsHTMLInputElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLInputElement");
};
goog.dom.asserts.assertIsHTMLTextAreaElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLTextAreaElement");
};
goog.dom.asserts.assertIsHTMLCanvasElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLCanvasElement");
};
goog.dom.asserts.assertIsHTMLEmbedElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLEmbedElement");
};
goog.dom.asserts.assertIsHTMLFormElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLFormElement");
};
goog.dom.asserts.assertIsHTMLFrameElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLFrameElement");
};
goog.dom.asserts.assertIsHTMLIFrameElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLIFrameElement");
};
goog.dom.asserts.assertIsHTMLObjectElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLObjectElement");
};
goog.dom.asserts.assertIsHTMLScriptElement = function(o) {
  return goog.dom.asserts.assertIsElementType_(o, "HTMLScriptElement");
};
goog.dom.asserts.debugStringForType_ = function(value) {
  if (goog.isObject(value)) {
    try {
      return value.constructor.displayName || value.constructor.name || Object.prototype.toString.call(value);
    } catch (e) {
      return "<object could not be stringified>";
    }
  } else {
    return void 0 === value ? "undefined" : null === value ? "null" : typeof value;
  }
};
goog.dom.asserts.getWindow_ = function(o) {
  try {
    var doc = o && o.ownerDocument, win = doc && (doc.defaultView || doc.parentWindow);
    win = win || goog.global;
    if (win.Element && win.Location) {
      return win;
    }
  } catch (ex) {
  }
  return null;
};
var module$exports$goog$labs$userAgent = {}, JSCompiler_inline_result$jscomp$36;
JSCompiler_inline_result$jscomp$36 = !1;
module$exports$goog$labs$userAgent.USE_CLIENT_HINTS = JSCompiler_inline_result$jscomp$36;
goog.string = {};
goog.string.internal = {};
goog.string.internal.startsWith = function(str, prefix) {
  return 0 == str.lastIndexOf(prefix, 0);
};
goog.string.internal.endsWith = function(str, suffix) {
  var l = str.length - suffix.length;
  return 0 <= l && str.indexOf(suffix, l) == l;
};
goog.string.internal.caseInsensitiveStartsWith = function(str, prefix) {
  return 0 == goog.string.internal.caseInsensitiveCompare(prefix, str.slice(0, prefix.length));
};
goog.string.internal.caseInsensitiveEndsWith = function(str, suffix) {
  return 0 == goog.string.internal.caseInsensitiveCompare(suffix, str.slice(str.length - suffix.length));
};
goog.string.internal.caseInsensitiveEquals = function(str1, str2) {
  return str1.toLowerCase() == str2.toLowerCase();
};
goog.string.internal.isEmptyOrWhitespace = function(str) {
  return /^[\s\xa0]*$/.test(str);
};
goog.string.internal.trim = goog.TRUSTED_SITE && String.prototype.trim ? function(str) {
  return str.trim();
} : function(str) {
  return /^[\s\xa0]*([\s\S]*?)[\s\xa0]*$/.exec(str)[1];
};
goog.string.internal.caseInsensitiveCompare = function(str1, str2) {
  var test1 = String(str1).toLowerCase(), test2 = String(str2).toLowerCase();
  return test1 < test2 ? -1 : test1 == test2 ? 0 : 1;
};
goog.string.internal.newLineToBr = function(str, opt_xml) {
  return str.replace(/(\r\n|\r|\n)/g, opt_xml ? "<br />" : "<br>");
};
goog.string.internal.htmlEscape = function(str, opt_isLikelyToContainHtmlChars) {
  if (opt_isLikelyToContainHtmlChars) {
    str = str.replace(goog.string.internal.AMP_RE_, "&amp;").replace(goog.string.internal.LT_RE_, "&lt;").replace(goog.string.internal.GT_RE_, "&gt;").replace(goog.string.internal.QUOT_RE_, "&quot;").replace(goog.string.internal.SINGLE_QUOTE_RE_, "&#39;").replace(goog.string.internal.NULL_RE_, "&#0;");
  } else {
    if (!goog.string.internal.ALL_RE_.test(str)) {
      return str;
    }
    -1 != str.indexOf("&") && (str = str.replace(goog.string.internal.AMP_RE_, "&amp;"));
    -1 != str.indexOf("<") && (str = str.replace(goog.string.internal.LT_RE_, "&lt;"));
    -1 != str.indexOf(">") && (str = str.replace(goog.string.internal.GT_RE_, "&gt;"));
    -1 != str.indexOf('"') && (str = str.replace(goog.string.internal.QUOT_RE_, "&quot;"));
    -1 != str.indexOf("'") && (str = str.replace(goog.string.internal.SINGLE_QUOTE_RE_, "&#39;"));
    -1 != str.indexOf("\x00") && (str = str.replace(goog.string.internal.NULL_RE_, "&#0;"));
  }
  return str;
};
goog.string.internal.AMP_RE_ = /&/g;
goog.string.internal.LT_RE_ = /</g;
goog.string.internal.GT_RE_ = />/g;
goog.string.internal.QUOT_RE_ = /"/g;
goog.string.internal.SINGLE_QUOTE_RE_ = /'/g;
goog.string.internal.NULL_RE_ = /\x00/g;
goog.string.internal.ALL_RE_ = /[\x00&<>"']/;
goog.string.internal.whitespaceEscape = function(str, opt_xml) {
  return goog.string.internal.newLineToBr(str.replace(/  /g, " &#160;"), opt_xml);
};
goog.string.internal.contains = function(str, subString) {
  return -1 != str.indexOf(subString);
};
goog.string.internal.caseInsensitiveContains = function(str, subString) {
  return goog.string.internal.contains(str.toLowerCase(), subString.toLowerCase());
};
goog.string.internal.compareVersions = function(version1, version2) {
  for (var order = 0, v1Subs = goog.string.internal.trim(String(version1)).split("."), v2Subs = goog.string.internal.trim(String(version2)).split("."), subCount = Math.max(v1Subs.length, v2Subs.length), subIdx = 0; 0 == order && subIdx < subCount; subIdx++) {
    var v1Sub = v1Subs[subIdx] || "", v2Sub = v2Subs[subIdx] || "";
    do {
      var v1Comp = /(\d*)(\D*)(.*)/.exec(v1Sub) || ["", "", "", ""], v2Comp = /(\d*)(\D*)(.*)/.exec(v2Sub) || ["", "", "", ""];
      if (0 == v1Comp[0].length && 0 == v2Comp[0].length) {
        break;
      }
      var v1CompNum = 0 == v1Comp[1].length ? 0 : parseInt(v1Comp[1], 10), v2CompNum = 0 == v2Comp[1].length ? 0 : parseInt(v2Comp[1], 10);
      order = goog.string.internal.compareElements_(v1CompNum, v2CompNum) || goog.string.internal.compareElements_(0 == v1Comp[2].length, 0 == v2Comp[2].length) || goog.string.internal.compareElements_(v1Comp[2], v2Comp[2]);
      v1Sub = v1Comp[3];
      v2Sub = v2Comp[3];
    } while (0 == order);
  }
  return order;
};
goog.string.internal.compareElements_ = function(left, right) {
  return left < right ? -1 : left > right ? 1 : 0;
};
goog.labs = {};
goog.labs.userAgent = {};
goog.labs.userAgent.util = {};
function module$contents$goog$labs$userAgent$util_getNativeUserAgentString() {
  var navigator = goog.global.navigator;
  if (navigator) {
    var userAgent = navigator.userAgent;
    if (userAgent) {
      return userAgent;
    }
  }
  return "";
}
function module$contents$goog$labs$userAgent$util_getNativeUserAgentData() {
  if (!module$exports$goog$labs$userAgent.USE_CLIENT_HINTS) {
    return null;
  }
  var navigator = goog.global.navigator;
  return navigator ? navigator.userAgentData || null : null;
}
var module$contents$goog$labs$userAgent$util_userAgentInternal = null, module$contents$goog$labs$userAgent$util_userAgentDataInternal = module$contents$goog$labs$userAgent$util_getNativeUserAgentData();
function module$contents$goog$labs$userAgent$util_setUserAgent(userAgent) {
  module$contents$goog$labs$userAgent$util_userAgentInternal = "string" === typeof userAgent ? userAgent : module$contents$goog$labs$userAgent$util_getNativeUserAgentString();
}
function module$contents$goog$labs$userAgent$util_getUserAgent() {
  return null == module$contents$goog$labs$userAgent$util_userAgentInternal ? module$contents$goog$labs$userAgent$util_getNativeUserAgentString() : module$contents$goog$labs$userAgent$util_userAgentInternal;
}
function module$contents$goog$labs$userAgent$util_setUserAgentData(userAgentData) {
  module$contents$goog$labs$userAgent$util_userAgentDataInternal = userAgentData;
}
function module$contents$goog$labs$userAgent$util_resetUserAgentData() {
  module$contents$goog$labs$userAgent$util_userAgentDataInternal = module$contents$goog$labs$userAgent$util_getNativeUserAgentData();
}
function module$contents$goog$labs$userAgent$util_getUserAgentData() {
  return module$contents$goog$labs$userAgent$util_userAgentDataInternal;
}
function module$contents$goog$labs$userAgent$util_matchUserAgentDataBrand(str) {
  var data = module$contents$goog$labs$userAgent$util_userAgentDataInternal;
  return data ? data.brands.some(function($jscomp$destructuring$var0) {
    var $jscomp$destructuring$var1 = $jscomp$destructuring$var0, brand = $jscomp$destructuring$var1.brand;
    return brand && (0,goog.string.internal.contains)(brand, str);
  }) : !1;
}
function module$contents$goog$labs$userAgent$util_matchUserAgent(str) {
  var userAgent = module$contents$goog$labs$userAgent$util_getUserAgent();
  return (0,goog.string.internal.contains)(userAgent, str);
}
function module$contents$goog$labs$userAgent$util_matchUserAgentIgnoreCase(str) {
  var userAgent = module$contents$goog$labs$userAgent$util_getUserAgent();
  return (0,goog.string.internal.caseInsensitiveContains)(userAgent, str);
}
function module$contents$goog$labs$userAgent$util_extractVersionTuples(userAgent) {
  for (var versionRegExp = RegExp("([A-Z][\\w ]+)/([^\\s]+)\\s*(?:\\((.*?)\\))?", "g"), data = [], match; match = versionRegExp.exec(userAgent);) {
    data.push([match[1], match[2], match[3] || void 0]);
  }
  return data;
}
goog.labs.userAgent.util.ASSUME_CLIENT_HINTS_SUPPORT = !1;
goog.labs.userAgent.util.extractVersionTuples = module$contents$goog$labs$userAgent$util_extractVersionTuples;
goog.labs.userAgent.util.getNativeUserAgentString = module$contents$goog$labs$userAgent$util_getNativeUserAgentString;
goog.labs.userAgent.util.getUserAgent = module$contents$goog$labs$userAgent$util_getUserAgent;
goog.labs.userAgent.util.getUserAgentData = module$contents$goog$labs$userAgent$util_getUserAgentData;
goog.labs.userAgent.util.matchUserAgent = module$contents$goog$labs$userAgent$util_matchUserAgent;
goog.labs.userAgent.util.matchUserAgentDataBrand = module$contents$goog$labs$userAgent$util_matchUserAgentDataBrand;
goog.labs.userAgent.util.matchUserAgentIgnoreCase = module$contents$goog$labs$userAgent$util_matchUserAgentIgnoreCase;
goog.labs.userAgent.util.resetUserAgentData = module$contents$goog$labs$userAgent$util_resetUserAgentData;
goog.labs.userAgent.util.setUserAgent = module$contents$goog$labs$userAgent$util_setUserAgent;
goog.labs.userAgent.util.setUserAgentData = module$contents$goog$labs$userAgent$util_setUserAgentData;
var module$exports$goog$labs$userAgent$highEntropy$highEntropyValue = {AsyncValue:function() {
}};
module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.AsyncValue.prototype.getIfLoaded = function() {
};
module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.AsyncValue.prototype.load = function() {
};
module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.HighEntropyValue = function(key) {
  this.key_ = key;
  this.promise_ = this.value_ = void 0;
  this.pending_ = !1;
};
module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.HighEntropyValue.prototype.getIfLoaded = function() {
  var userAgentData = module$contents$goog$labs$userAgent$util_userAgentDataInternal;
  if (userAgentData) {
    return this.value_;
  }
};
module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.HighEntropyValue.prototype.load = function() {
  var $jscomp$async$this = this, userAgentData;
  return $jscomp.asyncExecutePromiseGeneratorProgram(function($jscomp$generator$context) {
    if (1 == $jscomp$generator$context.nextAddress) {
      userAgentData = module$contents$goog$labs$userAgent$util_userAgentDataInternal;
      if (!userAgentData) {
        return $jscomp$generator$context.return(void 0);
      }
      $jscomp$async$this.promise_ || ($jscomp$async$this.pending_ = !0, $jscomp$async$this.promise_ = function() {
        var dataValues;
        return $jscomp.asyncExecutePromiseGeneratorProgram(function($jscomp$generator$context$1) {
          if (1 == $jscomp$generator$context$1.nextAddress) {
            return $jscomp$generator$context$1.setFinallyBlock(2), $jscomp$generator$context$1.yield(userAgentData.getHighEntropyValues([$jscomp$async$this.key_]), 4);
          }
          if (2 != $jscomp$generator$context$1.nextAddress) {
            return dataValues = $jscomp$generator$context$1.yieldResult, $jscomp$async$this.value_ = dataValues[$jscomp$async$this.key_], $jscomp$generator$context$1.return($jscomp$async$this.value_);
          }
          $jscomp$generator$context$1.enterFinallyBlock();
          $jscomp$async$this.pending_ = !1;
          return $jscomp$generator$context$1.leaveFinallyBlock(0);
        });
      }());
      return $jscomp$generator$context.yield($jscomp$async$this.promise_, 2);
    }
    return $jscomp$generator$context.return($jscomp$generator$context.yieldResult);
  });
};
module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.HighEntropyValue.prototype.resetForTesting = function() {
  if (this.pending_) {
    throw Error("Unsafe call to resetForTesting");
  }
  this.value_ = this.promise_ = void 0;
  this.pending_ = !1;
};
module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.Version = function(versionString) {
  this.versionString_ = versionString;
};
module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.Version.prototype.isAtLeast = function(version) {
  return 0 <= (0,goog.string.internal.compareVersions)(this.versionString_, version);
};
var module$exports$goog$labs$userAgent$highEntropy$highEntropyData = {};
module$exports$goog$labs$userAgent$highEntropy$highEntropyData.fullVersionList = new module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.HighEntropyValue("fullVersionList");
module$exports$goog$labs$userAgent$highEntropy$highEntropyData.platformVersion = new module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.HighEntropyValue("platformVersion");
function module$contents$goog$labs$userAgent$highEntropy$highEntropyData_resetAllForTesting() {
  module$exports$goog$labs$userAgent$highEntropy$highEntropyData.fullVersionList.resetForTesting();
  module$exports$goog$labs$userAgent$highEntropy$highEntropyData.platformVersion.resetForTesting();
}
module$exports$goog$labs$userAgent$highEntropy$highEntropyData.resetAllForTesting = module$contents$goog$labs$userAgent$highEntropy$highEntropyData_resetAllForTesting;
goog.labs.userAgent.browser = {};
var module$contents$goog$labs$userAgent$browser_Brand = {ANDROID_BROWSER:"Android Browser", CHROMIUM:"Chromium", EDGE:"Microsoft Edge", FIREFOX:"Firefox", IE:"Internet Explorer", OPERA:"Opera", SAFARI:"Safari", SILK:"Silk",};
goog.labs.userAgent.browser.Brand = module$contents$goog$labs$userAgent$browser_Brand;
function module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() {
  var userAgentData = module$contents$goog$labs$userAgent$util_userAgentDataInternal;
  return !!userAgentData && 0 < userAgentData.brands.length;
}
function module$contents$goog$labs$userAgent$browser_matchOpera() {
  return module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() ? !1 : module$contents$goog$labs$userAgent$util_matchUserAgent("Opera");
}
function module$contents$goog$labs$userAgent$browser_matchIE() {
  return module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() ? !1 : module$contents$goog$labs$userAgent$util_matchUserAgent("Trident") || module$contents$goog$labs$userAgent$util_matchUserAgent("MSIE");
}
function module$contents$goog$labs$userAgent$browser_matchEdgeHtml() {
  return module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() ? !1 : module$contents$goog$labs$userAgent$util_matchUserAgent("Edge");
}
function module$contents$goog$labs$userAgent$browser_matchEdgeChromium() {
  return module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() ? module$contents$goog$labs$userAgent$util_matchUserAgentDataBrand(module$contents$goog$labs$userAgent$browser_Brand.EDGE) : module$contents$goog$labs$userAgent$util_matchUserAgent("Edg/");
}
function module$contents$goog$labs$userAgent$browser_matchOperaChromium() {
  return module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() ? module$contents$goog$labs$userAgent$util_matchUserAgentDataBrand(module$contents$goog$labs$userAgent$browser_Brand.OPERA) : module$contents$goog$labs$userAgent$util_matchUserAgent("OPR");
}
function module$contents$goog$labs$userAgent$browser_matchFirefox() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("Firefox") || module$contents$goog$labs$userAgent$util_matchUserAgent("FxiOS");
}
function module$contents$goog$labs$userAgent$browser_matchSafari() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("Safari") && !(module$contents$goog$labs$userAgent$browser_matchChrome() || module$contents$goog$labs$userAgent$browser_matchCoast() || module$contents$goog$labs$userAgent$browser_matchOpera() || module$contents$goog$labs$userAgent$browser_matchEdgeHtml() || module$contents$goog$labs$userAgent$browser_matchEdgeChromium() || module$contents$goog$labs$userAgent$browser_matchOperaChromium() || module$contents$goog$labs$userAgent$browser_matchFirefox() || 
  module$contents$goog$labs$userAgent$browser_isSilk() || module$contents$goog$labs$userAgent$util_matchUserAgent("Android"));
}
function module$contents$goog$labs$userAgent$browser_matchCoast() {
  return module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() ? !1 : module$contents$goog$labs$userAgent$util_matchUserAgent("Coast");
}
function module$contents$goog$labs$userAgent$browser_matchIosWebview() {
  return (module$contents$goog$labs$userAgent$util_matchUserAgent("iPad") || module$contents$goog$labs$userAgent$util_matchUserAgent("iPhone")) && !module$contents$goog$labs$userAgent$browser_matchSafari() && !module$contents$goog$labs$userAgent$browser_matchChrome() && !module$contents$goog$labs$userAgent$browser_matchCoast() && !module$contents$goog$labs$userAgent$browser_matchFirefox() && module$contents$goog$labs$userAgent$util_matchUserAgent("AppleWebKit");
}
function module$contents$goog$labs$userAgent$browser_matchChrome() {
  return module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() ? module$contents$goog$labs$userAgent$util_matchUserAgentDataBrand(module$contents$goog$labs$userAgent$browser_Brand.CHROMIUM) : (module$contents$goog$labs$userAgent$util_matchUserAgent("Chrome") || module$contents$goog$labs$userAgent$util_matchUserAgent("CriOS")) && !module$contents$goog$labs$userAgent$browser_matchEdgeHtml() || module$contents$goog$labs$userAgent$browser_isSilk();
}
function module$contents$goog$labs$userAgent$browser_matchAndroidBrowser() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("Android") && !(module$contents$goog$labs$userAgent$browser_matchChrome() || module$contents$goog$labs$userAgent$browser_matchFirefox() || module$contents$goog$labs$userAgent$browser_matchOpera() || module$contents$goog$labs$userAgent$browser_isSilk());
}
goog.labs.userAgent.browser.isOpera = module$contents$goog$labs$userAgent$browser_matchOpera;
goog.labs.userAgent.browser.isIE = module$contents$goog$labs$userAgent$browser_matchIE;
goog.labs.userAgent.browser.isEdge = module$contents$goog$labs$userAgent$browser_matchEdgeHtml;
goog.labs.userAgent.browser.isEdgeChromium = module$contents$goog$labs$userAgent$browser_matchEdgeChromium;
goog.labs.userAgent.browser.isOperaChromium = module$contents$goog$labs$userAgent$browser_matchOperaChromium;
goog.labs.userAgent.browser.isFirefox = module$contents$goog$labs$userAgent$browser_matchFirefox;
goog.labs.userAgent.browser.isSafari = module$contents$goog$labs$userAgent$browser_matchSafari;
goog.labs.userAgent.browser.isCoast = module$contents$goog$labs$userAgent$browser_matchCoast;
goog.labs.userAgent.browser.isIosWebview = module$contents$goog$labs$userAgent$browser_matchIosWebview;
goog.labs.userAgent.browser.isChrome = module$contents$goog$labs$userAgent$browser_matchChrome;
goog.labs.userAgent.browser.isAndroidBrowser = module$contents$goog$labs$userAgent$browser_matchAndroidBrowser;
function module$contents$goog$labs$userAgent$browser_isSilk() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("Silk");
}
goog.labs.userAgent.browser.isSilk = module$contents$goog$labs$userAgent$browser_isSilk;
function module$contents$goog$labs$userAgent$browser_createVersionMap(versionTuples) {
  var versionMap = {};
  versionTuples.forEach(function(tuple) {
    var key = tuple[0], value = tuple[1];
    versionMap[key] = value;
  });
  return function(keys) {
    return versionMap[keys.find(function(key) {
      return key in versionMap;
    })] || "";
  };
}
function module$contents$goog$labs$userAgent$browser_getVersion() {
  var userAgentString = module$contents$goog$labs$userAgent$util_getUserAgent();
  if (module$contents$goog$labs$userAgent$browser_matchIE()) {
    return module$contents$goog$labs$userAgent$browser_getIEVersion(userAgentString);
  }
  var versionTuples = module$contents$goog$labs$userAgent$util_extractVersionTuples(userAgentString), lookUpValueWithKeys = module$contents$goog$labs$userAgent$browser_createVersionMap(versionTuples);
  if (module$contents$goog$labs$userAgent$browser_matchOpera()) {
    return lookUpValueWithKeys(["Version", "Opera"]);
  }
  if (module$contents$goog$labs$userAgent$browser_matchEdgeHtml()) {
    return lookUpValueWithKeys(["Edge"]);
  }
  if (module$contents$goog$labs$userAgent$browser_matchEdgeChromium()) {
    return lookUpValueWithKeys(["Edg"]);
  }
  if (module$contents$goog$labs$userAgent$browser_isSilk()) {
    return lookUpValueWithKeys(["Silk"]);
  }
  if (module$contents$goog$labs$userAgent$browser_matchChrome()) {
    return lookUpValueWithKeys(["Chrome", "CriOS", "HeadlessChrome"]);
  }
  var tuple = versionTuples[2];
  return tuple && tuple[1] || "";
}
goog.labs.userAgent.browser.getVersion = module$contents$goog$labs$userAgent$browser_getVersion;
function module$contents$goog$labs$userAgent$browser_isVersionOrHigher(version) {
  return 0 <= (0,goog.string.internal.compareVersions)(module$contents$goog$labs$userAgent$browser_getVersion(), version);
}
goog.labs.userAgent.browser.isVersionOrHigher = module$contents$goog$labs$userAgent$browser_isVersionOrHigher;
function module$contents$goog$labs$userAgent$browser_getIEVersion(userAgent) {
  var rv = /rv: *([\d\.]*)/.exec(userAgent);
  if (rv && rv[1]) {
    return rv[1];
  }
  var version = "", msie = /MSIE +([\d\.]+)/.exec(userAgent);
  if (msie && msie[1]) {
    var tridentVersion = /Trident\/(\d.\d)/.exec(userAgent);
    if ("7.0" == msie[1]) {
      if (tridentVersion && tridentVersion[1]) {
        switch(tridentVersion[1]) {
          case "4.0":
            version = "8.0";
            break;
          case "5.0":
            version = "9.0";
            break;
          case "6.0":
            version = "10.0";
            break;
          case "7.0":
            version = "11.0";
        }
      } else {
        version = "7.0";
      }
    } else {
      version = msie[1];
    }
  }
  return version;
}
function module$contents$goog$labs$userAgent$browser_getFullVersionFromUserAgentString(browser) {
  var userAgentString = module$contents$goog$labs$userAgent$util_getUserAgent();
  if (browser === module$contents$goog$labs$userAgent$browser_Brand.IE) {
    return module$contents$goog$labs$userAgent$browser_matchIE() ? module$contents$goog$labs$userAgent$browser_getIEVersion(userAgentString) : "";
  }
  var versionTuples = module$contents$goog$labs$userAgent$util_extractVersionTuples(userAgentString), lookUpValueWithKeys = module$contents$goog$labs$userAgent$browser_createVersionMap(versionTuples);
  switch(browser) {
    case module$contents$goog$labs$userAgent$browser_Brand.OPERA:
      if (module$contents$goog$labs$userAgent$browser_matchOpera()) {
        return lookUpValueWithKeys(["Version", "Opera"]);
      }
      if (module$contents$goog$labs$userAgent$browser_matchOperaChromium()) {
        return lookUpValueWithKeys(["OPR"]);
      }
      break;
    case module$contents$goog$labs$userAgent$browser_Brand.EDGE:
      if (module$contents$goog$labs$userAgent$browser_matchEdgeHtml()) {
        return lookUpValueWithKeys(["Edge"]);
      }
      if (module$contents$goog$labs$userAgent$browser_matchEdgeChromium()) {
        return lookUpValueWithKeys(["Edg"]);
      }
      break;
    case module$contents$goog$labs$userAgent$browser_Brand.CHROMIUM:
      if (module$contents$goog$labs$userAgent$browser_matchChrome()) {
        return lookUpValueWithKeys(["Chrome", "CriOS", "HeadlessChrome"]);
      }
  }
  if (browser === module$contents$goog$labs$userAgent$browser_Brand.FIREFOX && module$contents$goog$labs$userAgent$browser_matchFirefox() || browser === module$contents$goog$labs$userAgent$browser_Brand.SAFARI && module$contents$goog$labs$userAgent$browser_matchSafari() || browser === module$contents$goog$labs$userAgent$browser_Brand.ANDROID_BROWSER && module$contents$goog$labs$userAgent$browser_matchAndroidBrowser() || browser === module$contents$goog$labs$userAgent$browser_Brand.SILK && module$contents$goog$labs$userAgent$browser_isSilk()) {
    var tuple = versionTuples[2];
    return tuple && tuple[1] || "";
  }
  return "";
}
function module$contents$goog$labs$userAgent$browser_versionOf_(browser) {
  if (module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() && browser !== module$contents$goog$labs$userAgent$browser_Brand.SILK) {
    var data = module$contents$goog$labs$userAgent$util_userAgentDataInternal, matchingBrand = data.brands.find(function($jscomp$destructuring$var2) {
      var $jscomp$destructuring$var3 = $jscomp$destructuring$var2, brand = $jscomp$destructuring$var3.brand;
      return brand === browser;
    });
    if (!matchingBrand || !matchingBrand.version) {
      return NaN;
    }
    var versionParts = matchingBrand.version.split(".");
  } else {
    var fullVersion = module$contents$goog$labs$userAgent$browser_getFullVersionFromUserAgentString(browser);
    if ("" === fullVersion) {
      return NaN;
    }
    versionParts = fullVersion.split(".");
  }
  if (0 === versionParts.length) {
    return NaN;
  }
  var majorVersion = versionParts[0];
  return Number(majorVersion);
}
function module$contents$goog$labs$userAgent$browser_isAtLeast(brand, majorVersion) {
  goog.asserts.assert(Math.floor(majorVersion) === majorVersion, "Major version must be an integer");
  return module$contents$goog$labs$userAgent$browser_versionOf_(brand) >= majorVersion;
}
goog.labs.userAgent.browser.isAtLeast = module$contents$goog$labs$userAgent$browser_isAtLeast;
function module$contents$goog$labs$userAgent$browser_isAtMost(brand, majorVersion) {
  goog.asserts.assert(Math.floor(majorVersion) === majorVersion, "Major version must be an integer");
  return module$contents$goog$labs$userAgent$browser_versionOf_(brand) <= majorVersion;
}
goog.labs.userAgent.browser.isAtMost = module$contents$goog$labs$userAgent$browser_isAtMost;
var module$contents$goog$labs$userAgent$browser_HighEntropyBrandVersion = function(brand) {
  this.brand_ = brand;
};
module$contents$goog$labs$userAgent$browser_HighEntropyBrandVersion.prototype.getIfLoaded = function() {
  var $jscomp$this = this, loadedVersionList = module$exports$goog$labs$userAgent$highEntropy$highEntropyData.fullVersionList.getIfLoaded();
  if (void 0 !== loadedVersionList) {
    var matchingBrand = loadedVersionList.find(function($jscomp$destructuring$var4) {
      var $jscomp$destructuring$var5 = $jscomp$destructuring$var4, brand = $jscomp$destructuring$var5.brand;
      return $jscomp$this.brand_ === brand;
    });
    goog.asserts.assertExists(matchingBrand);
    return new module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.Version(matchingBrand.version);
  }
};
module$contents$goog$labs$userAgent$browser_HighEntropyBrandVersion.prototype.load = function() {
  var $jscomp$async$this = this, loadedVersionList, matchingBrand;
  return $jscomp.asyncExecutePromiseGeneratorProgram(function($jscomp$generator$context) {
    if (1 == $jscomp$generator$context.nextAddress) {
      return $jscomp$generator$context.yield(module$exports$goog$labs$userAgent$highEntropy$highEntropyData.fullVersionList.load(), 2);
    }
    loadedVersionList = $jscomp$generator$context.yieldResult;
    matchingBrand = loadedVersionList.find(function($jscomp$destructuring$var6) {
      var $jscomp$destructuring$var7 = $jscomp$destructuring$var6, brand = $jscomp$destructuring$var7.brand;
      return $jscomp$async$this.brand_ === brand;
    });
    goog.asserts.assertExists(matchingBrand);
    return $jscomp$generator$context.return(new module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.Version(matchingBrand.version));
  });
};
var module$contents$goog$labs$userAgent$browser_UserAgentStringFallbackBrandVersion = function(versionString) {
  this.version_ = new module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.Version(versionString);
};
module$contents$goog$labs$userAgent$browser_UserAgentStringFallbackBrandVersion.prototype.getIfLoaded = function() {
  return this.version_;
};
module$contents$goog$labs$userAgent$browser_UserAgentStringFallbackBrandVersion.prototype.load = function() {
  var $jscomp$async$this = this;
  return $jscomp.asyncExecutePromiseGeneratorProgram(function($jscomp$generator$context) {
    return $jscomp$generator$context.return($jscomp$async$this.version_);
  });
};
function module$contents$goog$labs$userAgent$browser_loadFullVersions() {
  return $jscomp.asyncExecutePromiseGeneratorProgram(function($jscomp$generator$context) {
    return module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() && module$contents$goog$labs$userAgent$browser_isAtLeast(module$contents$goog$labs$userAgent$browser_Brand.CHROMIUM, 98) ? $jscomp$generator$context.yield(module$exports$goog$labs$userAgent$highEntropy$highEntropyData.fullVersionList.load(), 0) : $jscomp$generator$context.jumpTo(0);
  });
}
goog.labs.userAgent.browser.loadFullVersions = module$contents$goog$labs$userAgent$browser_loadFullVersions;
function module$contents$goog$labs$userAgent$browser_fullVersionOf(browser) {
  if (module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand() && module$contents$goog$labs$userAgent$browser_isAtLeast(module$contents$goog$labs$userAgent$browser_Brand.CHROMIUM, 98)) {
    var data = module$contents$goog$labs$userAgent$util_userAgentDataInternal;
    return data.brands.find(function($jscomp$destructuring$var8) {
      var $jscomp$destructuring$var9 = $jscomp$destructuring$var8, brand = $jscomp$destructuring$var9.brand;
      return brand === browser;
    }) ? new module$contents$goog$labs$userAgent$browser_HighEntropyBrandVersion(browser) : void 0;
  }
  var fullVersionFromUserAgentString = module$contents$goog$labs$userAgent$browser_getFullVersionFromUserAgentString(browser);
  return "" === fullVersionFromUserAgentString ? void 0 : new module$contents$goog$labs$userAgent$browser_UserAgentStringFallbackBrandVersion(fullVersionFromUserAgentString);
}
goog.labs.userAgent.browser.fullVersionOf = module$contents$goog$labs$userAgent$browser_fullVersionOf;
function module$contents$goog$labs$userAgent$browser_getVersionStringForLogging(browser) {
  if (module$contents$goog$labs$userAgent$browser_useUserAgentDataBrand()) {
    var fullVersionObj = module$contents$goog$labs$userAgent$browser_fullVersionOf(browser);
    if (fullVersionObj) {
      var fullVersion = fullVersionObj.getIfLoaded();
      if (fullVersion) {
        return fullVersion.versionString_;
      }
      var data = module$contents$goog$labs$userAgent$util_userAgentDataInternal, matchingBrand = data.brands.find(function($jscomp$destructuring$var10) {
        var $jscomp$destructuring$var11 = $jscomp$destructuring$var10, brand = $jscomp$destructuring$var11.brand;
        return brand === browser;
      });
      goog.asserts.assertExists(matchingBrand);
      return matchingBrand.version;
    }
    return "";
  }
  return module$contents$goog$labs$userAgent$browser_getFullVersionFromUserAgentString(browser);
}
goog.labs.userAgent.browser.getVersionStringForLogging = module$contents$goog$labs$userAgent$browser_getVersionStringForLogging;
goog.labs.userAgent.engine = {};
function module$contents$goog$labs$userAgent$engine_isPresto() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("Presto");
}
function module$contents$goog$labs$userAgent$engine_isTrident() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("Trident") || module$contents$goog$labs$userAgent$util_matchUserAgent("MSIE");
}
function module$contents$goog$labs$userAgent$engine_isEdge() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("Edge");
}
function module$contents$goog$labs$userAgent$engine_isWebKit() {
  return module$contents$goog$labs$userAgent$util_matchUserAgentIgnoreCase("WebKit") && !module$contents$goog$labs$userAgent$engine_isEdge();
}
function module$contents$goog$labs$userAgent$engine_isGecko() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("Gecko") && !module$contents$goog$labs$userAgent$engine_isWebKit() && !module$contents$goog$labs$userAgent$engine_isTrident() && !module$contents$goog$labs$userAgent$engine_isEdge();
}
function module$contents$goog$labs$userAgent$engine_getVersion() {
  var userAgentString = module$contents$goog$labs$userAgent$util_getUserAgent();
  if (userAgentString) {
    var tuples = module$contents$goog$labs$userAgent$util_extractVersionTuples(userAgentString);
    a: {
      if (module$contents$goog$labs$userAgent$engine_isEdge()) {
        for (var i = 0; i < tuples.length; i++) {
          var tuple = tuples[i];
          if ("Edge" == tuple[0]) {
            var JSCompiler_inline_result = tuple;
            break a;
          }
        }
        JSCompiler_inline_result = void 0;
      } else {
        JSCompiler_inline_result = tuples[1];
      }
    }
    var engineTuple = JSCompiler_inline_result;
    if (engineTuple) {
      return "Gecko" == engineTuple[0] ? module$contents$goog$labs$userAgent$engine_getVersionForKey(tuples, "Firefox") : engineTuple[1];
    }
    var browserTuple = tuples[0], info;
    if (browserTuple && (info = browserTuple[2])) {
      var match = /Trident\/([^\s;]+)/.exec(info);
      if (match) {
        return match[1];
      }
    }
  }
  return "";
}
function module$contents$goog$labs$userAgent$engine_isVersionOrHigher(version) {
  return 0 <= goog.string.internal.compareVersions(module$contents$goog$labs$userAgent$engine_getVersion(), version);
}
function module$contents$goog$labs$userAgent$engine_getVersionForKey(tuples, key) {
  var pair = module$contents$goog$array_find(tuples, function(pair) {
    return key == pair[0];
  });
  return pair && pair[1] || "";
}
goog.labs.userAgent.engine.getVersion = module$contents$goog$labs$userAgent$engine_getVersion;
goog.labs.userAgent.engine.isEdge = module$contents$goog$labs$userAgent$engine_isEdge;
goog.labs.userAgent.engine.isGecko = module$contents$goog$labs$userAgent$engine_isGecko;
goog.labs.userAgent.engine.isPresto = module$contents$goog$labs$userAgent$engine_isPresto;
goog.labs.userAgent.engine.isTrident = module$contents$goog$labs$userAgent$engine_isTrident;
goog.labs.userAgent.engine.isVersionOrHigher = module$contents$goog$labs$userAgent$engine_isVersionOrHigher;
goog.labs.userAgent.engine.isWebKit = module$contents$goog$labs$userAgent$engine_isWebKit;
goog.labs.userAgent.platform = {};
function module$contents$goog$labs$userAgent$platform_useUserAgentDataPlatform() {
  var userAgentData = module$contents$goog$labs$userAgent$util_userAgentDataInternal;
  return !!userAgentData && !!userAgentData.platform;
}
function module$contents$goog$labs$userAgent$platform_isAndroid() {
  return module$contents$goog$labs$userAgent$platform_useUserAgentDataPlatform() ? "Android" === module$contents$goog$labs$userAgent$util_userAgentDataInternal.platform : module$contents$goog$labs$userAgent$util_matchUserAgent("Android");
}
function module$contents$goog$labs$userAgent$platform_isIpod() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("iPod");
}
function module$contents$goog$labs$userAgent$platform_isIphone() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("iPhone") && !module$contents$goog$labs$userAgent$util_matchUserAgent("iPod") && !module$contents$goog$labs$userAgent$util_matchUserAgent("iPad");
}
function module$contents$goog$labs$userAgent$platform_isIpad() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("iPad");
}
function module$contents$goog$labs$userAgent$platform_isIos() {
  return module$contents$goog$labs$userAgent$platform_isIphone() || module$contents$goog$labs$userAgent$platform_isIpad() || module$contents$goog$labs$userAgent$platform_isIpod();
}
function module$contents$goog$labs$userAgent$platform_isMacintosh() {
  return module$contents$goog$labs$userAgent$platform_useUserAgentDataPlatform() ? "macOS" === module$contents$goog$labs$userAgent$util_userAgentDataInternal.platform : module$contents$goog$labs$userAgent$util_matchUserAgent("Macintosh");
}
function module$contents$goog$labs$userAgent$platform_isLinux() {
  return module$contents$goog$labs$userAgent$platform_useUserAgentDataPlatform() ? "Linux" === module$contents$goog$labs$userAgent$util_userAgentDataInternal.platform : module$contents$goog$labs$userAgent$util_matchUserAgent("Linux");
}
function module$contents$goog$labs$userAgent$platform_isWindows() {
  return module$contents$goog$labs$userAgent$platform_useUserAgentDataPlatform() ? "Windows" === module$contents$goog$labs$userAgent$util_userAgentDataInternal.platform : module$contents$goog$labs$userAgent$util_matchUserAgent("Windows");
}
function module$contents$goog$labs$userAgent$platform_isChromeOS() {
  return module$contents$goog$labs$userAgent$platform_useUserAgentDataPlatform() ? "Chrome OS" === module$contents$goog$labs$userAgent$util_userAgentDataInternal.platform : module$contents$goog$labs$userAgent$util_matchUserAgent("CrOS");
}
function module$contents$goog$labs$userAgent$platform_isChromecast() {
  return module$contents$goog$labs$userAgent$util_matchUserAgent("CrKey");
}
function module$contents$goog$labs$userAgent$platform_isKaiOS() {
  return module$contents$goog$labs$userAgent$util_matchUserAgentIgnoreCase("KaiOS");
}
function module$contents$goog$labs$userAgent$platform_getVersion() {
  var userAgentString = module$contents$goog$labs$userAgent$util_getUserAgent(), version = "";
  if (module$contents$goog$labs$userAgent$platform_isWindows()) {
    var re = /Windows (?:NT|Phone) ([0-9.]+)/;
    var match = re.exec(userAgentString);
    version = match ? match[1] : "0.0";
  } else if (module$contents$goog$labs$userAgent$platform_isIos()) {
    re = /(?:iPhone|iPod|iPad|CPU)\s+OS\s+(\S+)/;
    var match$10 = re.exec(userAgentString);
    version = match$10 && match$10[1].replace(/_/g, ".");
  } else if (module$contents$goog$labs$userAgent$platform_isMacintosh()) {
    re = /Mac OS X ([0-9_.]+)/;
    var match$11 = re.exec(userAgentString);
    version = match$11 ? match$11[1].replace(/_/g, ".") : "10";
  } else if (module$contents$goog$labs$userAgent$platform_isKaiOS()) {
    re = /(?:KaiOS)\/(\S+)/i;
    var match$12 = re.exec(userAgentString);
    version = match$12 && match$12[1];
  } else if (module$contents$goog$labs$userAgent$platform_isAndroid()) {
    re = /Android\s+([^\);]+)(\)|;)/;
    var match$13 = re.exec(userAgentString);
    version = match$13 && match$13[1];
  } else if (module$contents$goog$labs$userAgent$platform_isChromeOS()) {
    re = /(?:CrOS\s+(?:i686|x86_64)\s+([0-9.]+))/;
    var match$14 = re.exec(userAgentString);
    version = match$14 && match$14[1];
  }
  return version || "";
}
function module$contents$goog$labs$userAgent$platform_isVersionOrHigher(version) {
  return 0 <= goog.string.internal.compareVersions(module$contents$goog$labs$userAgent$platform_getVersion(), version);
}
var module$contents$goog$labs$userAgent$platform_PlatformVersion = function() {
};
module$contents$goog$labs$userAgent$platform_PlatformVersion.prototype.getIfLoaded = function() {
  if (module$contents$goog$labs$userAgent$util_userAgentDataInternal) {
    var loadedPlatformVersion = module$exports$goog$labs$userAgent$highEntropy$highEntropyData.platformVersion.getIfLoaded();
    if (void 0 !== loadedPlatformVersion) {
      return new module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.Version(loadedPlatformVersion);
    }
  } else {
    return new module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.Version(module$contents$goog$labs$userAgent$platform_getVersion());
  }
};
module$contents$goog$labs$userAgent$platform_PlatformVersion.prototype.load = function() {
  var JSCompiler_temp_const;
  return $jscomp.asyncExecutePromiseGeneratorProgram(function($jscomp$generator$context) {
    if (1 == $jscomp$generator$context.nextAddress) {
      if (!module$contents$goog$labs$userAgent$util_userAgentDataInternal) {
        return $jscomp$generator$context.return(new module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.Version(module$contents$goog$labs$userAgent$platform_getVersion()));
      }
      JSCompiler_temp_const = module$exports$goog$labs$userAgent$highEntropy$highEntropyValue.Version;
      return $jscomp$generator$context.yield(module$exports$goog$labs$userAgent$highEntropy$highEntropyData.platformVersion.load(), 3);
    }
    return $jscomp$generator$context.return(new JSCompiler_temp_const($jscomp$generator$context.yieldResult));
  });
};
var module$contents$goog$labs$userAgent$platform_version = new module$contents$goog$labs$userAgent$platform_PlatformVersion();
goog.labs.userAgent.platform.getVersion = module$contents$goog$labs$userAgent$platform_getVersion;
goog.labs.userAgent.platform.isAndroid = module$contents$goog$labs$userAgent$platform_isAndroid;
goog.labs.userAgent.platform.isChromeOS = module$contents$goog$labs$userAgent$platform_isChromeOS;
goog.labs.userAgent.platform.isChromecast = module$contents$goog$labs$userAgent$platform_isChromecast;
goog.labs.userAgent.platform.isIos = module$contents$goog$labs$userAgent$platform_isIos;
goog.labs.userAgent.platform.isIpad = module$contents$goog$labs$userAgent$platform_isIpad;
goog.labs.userAgent.platform.isIphone = module$contents$goog$labs$userAgent$platform_isIphone;
goog.labs.userAgent.platform.isIpod = module$contents$goog$labs$userAgent$platform_isIpod;
goog.labs.userAgent.platform.isKaiOS = module$contents$goog$labs$userAgent$platform_isKaiOS;
goog.labs.userAgent.platform.isLinux = module$contents$goog$labs$userAgent$platform_isLinux;
goog.labs.userAgent.platform.isMacintosh = module$contents$goog$labs$userAgent$platform_isMacintosh;
goog.labs.userAgent.platform.isVersionOrHigher = module$contents$goog$labs$userAgent$platform_isVersionOrHigher;
goog.labs.userAgent.platform.isWindows = module$contents$goog$labs$userAgent$platform_isWindows;
goog.labs.userAgent.platform.version = module$contents$goog$labs$userAgent$platform_version;
goog.reflect = {};
goog.reflect.object = function(type, object) {
  return object;
};
goog.reflect.objectProperty = function(prop) {
  return prop;
};
goog.reflect.sinkValue = function(x) {
  goog.reflect.sinkValue[" "](x);
  return x;
};
goog.reflect.sinkValue[" "] = function() {
};
goog.reflect.canAccessProperty = function(obj, prop) {
  try {
    return goog.reflect.sinkValue(obj[prop]), !0;
  } catch (e) {
  }
  return !1;
};
goog.reflect.cache = function(cacheObj, key, valueFn, opt_keyFn) {
  var storedKey = opt_keyFn ? opt_keyFn(key) : key;
  return Object.prototype.hasOwnProperty.call(cacheObj, storedKey) ? cacheObj[storedKey] : cacheObj[storedKey] = valueFn(key);
};
goog.userAgent = {};
goog.userAgent.ASSUME_IE = !1;
goog.userAgent.ASSUME_EDGE = !1;
goog.userAgent.ASSUME_GECKO = !1;
goog.userAgent.ASSUME_WEBKIT = !1;
goog.userAgent.ASSUME_MOBILE_WEBKIT = !1;
goog.userAgent.ASSUME_OPERA = !1;
goog.userAgent.ASSUME_ANY_VERSION = !1;
goog.userAgent.BROWSER_KNOWN_ = goog.userAgent.ASSUME_IE || goog.userAgent.ASSUME_EDGE || goog.userAgent.ASSUME_GECKO || goog.userAgent.ASSUME_MOBILE_WEBKIT || goog.userAgent.ASSUME_WEBKIT || goog.userAgent.ASSUME_OPERA;
goog.userAgent.getUserAgentString = function() {
  return module$contents$goog$labs$userAgent$util_getUserAgent();
};
goog.userAgent.getNavigatorTyped = function() {
  return goog.global.navigator || null;
};
goog.userAgent.getNavigator = function() {
  return goog.userAgent.getNavigatorTyped();
};
goog.userAgent.OPERA = goog.userAgent.BROWSER_KNOWN_ ? goog.userAgent.ASSUME_OPERA : module$contents$goog$labs$userAgent$browser_matchOpera();
goog.userAgent.IE = goog.userAgent.BROWSER_KNOWN_ ? goog.userAgent.ASSUME_IE : module$contents$goog$labs$userAgent$browser_matchIE();
goog.userAgent.EDGE = goog.userAgent.BROWSER_KNOWN_ ? goog.userAgent.ASSUME_EDGE : module$contents$goog$labs$userAgent$engine_isEdge();
goog.userAgent.EDGE_OR_IE = goog.userAgent.EDGE || goog.userAgent.IE;
goog.userAgent.GECKO = goog.userAgent.BROWSER_KNOWN_ ? goog.userAgent.ASSUME_GECKO : module$contents$goog$labs$userAgent$engine_isGecko();
goog.userAgent.WEBKIT = goog.userAgent.BROWSER_KNOWN_ ? goog.userAgent.ASSUME_WEBKIT || goog.userAgent.ASSUME_MOBILE_WEBKIT : module$contents$goog$labs$userAgent$engine_isWebKit();
goog.userAgent.isMobile_ = function() {
  return goog.userAgent.WEBKIT && module$contents$goog$labs$userAgent$util_matchUserAgent("Mobile");
};
goog.userAgent.MOBILE = goog.userAgent.ASSUME_MOBILE_WEBKIT || goog.userAgent.isMobile_();
goog.userAgent.SAFARI = goog.userAgent.WEBKIT;
goog.userAgent.determinePlatform_ = function() {
  var navigator = goog.userAgent.getNavigatorTyped();
  return navigator && navigator.platform || "";
};
goog.userAgent.PLATFORM = goog.userAgent.determinePlatform_();
goog.userAgent.ASSUME_MAC = !1;
goog.userAgent.ASSUME_WINDOWS = !1;
goog.userAgent.ASSUME_LINUX = !1;
goog.userAgent.ASSUME_X11 = !1;
goog.userAgent.ASSUME_ANDROID = !1;
goog.userAgent.ASSUME_IPHONE = !1;
goog.userAgent.ASSUME_IPAD = !1;
goog.userAgent.ASSUME_IPOD = !1;
goog.userAgent.ASSUME_KAIOS = !1;
goog.userAgent.PLATFORM_KNOWN_ = goog.userAgent.ASSUME_MAC || goog.userAgent.ASSUME_WINDOWS || goog.userAgent.ASSUME_LINUX || goog.userAgent.ASSUME_X11 || goog.userAgent.ASSUME_ANDROID || goog.userAgent.ASSUME_IPHONE || goog.userAgent.ASSUME_IPAD || goog.userAgent.ASSUME_IPOD;
goog.userAgent.MAC = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_MAC : module$contents$goog$labs$userAgent$platform_isMacintosh();
goog.userAgent.WINDOWS = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_WINDOWS : module$contents$goog$labs$userAgent$platform_isWindows();
goog.userAgent.isLegacyLinux_ = function() {
  return module$contents$goog$labs$userAgent$platform_isLinux() || module$contents$goog$labs$userAgent$platform_isChromeOS();
};
goog.userAgent.LINUX = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_LINUX : goog.userAgent.isLegacyLinux_();
goog.userAgent.isX11_ = function() {
  var navigator = goog.userAgent.getNavigatorTyped();
  return !!navigator && goog.string.internal.contains(navigator.appVersion || "", "X11");
};
goog.userAgent.X11 = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_X11 : goog.userAgent.isX11_();
goog.userAgent.ANDROID = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_ANDROID : module$contents$goog$labs$userAgent$platform_isAndroid();
goog.userAgent.IPHONE = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_IPHONE : module$contents$goog$labs$userAgent$platform_isIphone();
goog.userAgent.IPAD = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_IPAD : module$contents$goog$labs$userAgent$platform_isIpad();
goog.userAgent.IPOD = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_IPOD : module$contents$goog$labs$userAgent$platform_isIpod();
goog.userAgent.IOS = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_IPHONE || goog.userAgent.ASSUME_IPAD || goog.userAgent.ASSUME_IPOD : module$contents$goog$labs$userAgent$platform_isIos();
goog.userAgent.KAIOS = goog.userAgent.PLATFORM_KNOWN_ ? goog.userAgent.ASSUME_KAIOS : module$contents$goog$labs$userAgent$platform_isKaiOS();
goog.userAgent.determineVersion_ = function() {
  var version = "", arr = goog.userAgent.getVersionRegexResult_();
  arr && (version = arr ? arr[1] : "");
  if (goog.userAgent.IE) {
    var docMode = goog.userAgent.getDocumentMode_();
    if (null != docMode && docMode > parseFloat(version)) {
      return String(docMode);
    }
  }
  return version;
};
goog.userAgent.getVersionRegexResult_ = function() {
  var userAgent = goog.userAgent.getUserAgentString();
  if (goog.userAgent.GECKO) {
    return /rv:([^\);]+)(\)|;)/.exec(userAgent);
  }
  if (goog.userAgent.EDGE) {
    return /Edge\/([\d\.]+)/.exec(userAgent);
  }
  if (goog.userAgent.IE) {
    return /\b(?:MSIE|rv)[: ]([^\);]+)(\)|;)/.exec(userAgent);
  }
  if (goog.userAgent.WEBKIT) {
    return /WebKit\/(\S+)/.exec(userAgent);
  }
  if (goog.userAgent.OPERA) {
    return /(?:Version)[ \/]?(\S+)/.exec(userAgent);
  }
};
goog.userAgent.getDocumentMode_ = function() {
  var doc = goog.global.document;
  return doc ? doc.documentMode : void 0;
};
goog.userAgent.VERSION = goog.userAgent.determineVersion_();
goog.userAgent.compare = function(v1, v2) {
  return goog.string.internal.compareVersions(v1, v2);
};
goog.userAgent.isVersionOrHigherCache_ = {};
goog.userAgent.isVersionOrHigher = function(version) {
  return goog.userAgent.ASSUME_ANY_VERSION || goog.reflect.cache(goog.userAgent.isVersionOrHigherCache_, version, function() {
    return 0 <= goog.string.internal.compareVersions(goog.userAgent.VERSION, version);
  });
};
goog.userAgent.isDocumentModeOrHigher = function(documentMode) {
  return Number(goog.userAgent.DOCUMENT_MODE) >= documentMode;
};
goog.userAgent.isDocumentMode = goog.userAgent.isDocumentModeOrHigher;
var JSCompiler_inline_result$jscomp$72;
var doc$jscomp$inline_78 = goog.global.document;
if (doc$jscomp$inline_78 && goog.userAgent.IE) {
  var documentMode$jscomp$inline_79 = goog.userAgent.getDocumentMode_();
  if (documentMode$jscomp$inline_79) {
    JSCompiler_inline_result$jscomp$72 = documentMode$jscomp$inline_79;
  } else {
    var ieVersion$jscomp$inline_80 = parseInt(goog.userAgent.VERSION, 10);
    JSCompiler_inline_result$jscomp$72 = ieVersion$jscomp$inline_80 || void 0;
  }
} else {
  JSCompiler_inline_result$jscomp$72 = void 0;
}
goog.userAgent.DOCUMENT_MODE = JSCompiler_inline_result$jscomp$72;
goog.dom.BrowserFeature = {};
goog.dom.BrowserFeature.ASSUME_NO_OFFSCREEN_CANVAS = !1;
goog.dom.BrowserFeature.ASSUME_OFFSCREEN_CANVAS = !1;
goog.dom.BrowserFeature.detectOffscreenCanvas_ = function(contextName) {
  try {
    return !!(new self.OffscreenCanvas(0, 0)).getContext(contextName);
  } catch (ex) {
  }
  return !1;
};
goog.dom.BrowserFeature.OFFSCREEN_CANVAS_2D = !goog.dom.BrowserFeature.ASSUME_NO_OFFSCREEN_CANVAS && (goog.dom.BrowserFeature.ASSUME_OFFSCREEN_CANVAS || goog.dom.BrowserFeature.detectOffscreenCanvas_("2d"));
goog.dom.BrowserFeature.CAN_ADD_NAME_OR_TYPE_ATTRIBUTES = !0;
goog.dom.BrowserFeature.CAN_USE_CHILDREN_ATTRIBUTE = !0;
goog.dom.BrowserFeature.CAN_USE_INNER_TEXT = !1;
goog.dom.BrowserFeature.CAN_USE_PARENT_ELEMENT_PROPERTY = goog.userAgent.IE || goog.userAgent.WEBKIT;
goog.dom.BrowserFeature.INNER_HTML_NEEDS_SCOPED_ELEMENT = goog.userAgent.IE;
goog.functions = {};
goog.functions.constant = function(retValue) {
  return function() {
    return retValue;
  };
};
goog.functions.FALSE = function() {
  return !1;
};
goog.functions.TRUE = function() {
  return !0;
};
goog.functions.NULL = function() {
  return null;
};
goog.functions.UNDEFINED = function() {
};
goog.functions.EMPTY = goog.functions.UNDEFINED;
goog.functions.identity = function(opt_returnValue) {
  return opt_returnValue;
};
goog.functions.error = function(message) {
  return function() {
    throw Error(message);
  };
};
goog.functions.fail = function(err) {
  return function() {
    throw err;
  };
};
goog.functions.lock = function(f, opt_numArgs) {
  opt_numArgs = opt_numArgs || 0;
  return function() {
    var self = this;
    return f.apply(self, Array.prototype.slice.call(arguments, 0, opt_numArgs));
  };
};
goog.functions.nth = function(n) {
  return function() {
    return arguments[n];
  };
};
goog.functions.partialRight = function(fn, var_args) {
  var rightArgs = Array.prototype.slice.call(arguments, 1);
  return function() {
    var self = this;
    self === goog.global && (self = void 0);
    var newArgs = Array.prototype.slice.call(arguments);
    newArgs.push.apply(newArgs, rightArgs);
    return fn.apply(self, newArgs);
  };
};
goog.functions.withReturnValue = function(f, retValue) {
  return goog.functions.sequence(f, goog.functions.constant(retValue));
};
goog.functions.equalTo = function(value, opt_useLooseComparison) {
  return function(other) {
    return opt_useLooseComparison ? value == other : value === other;
  };
};
goog.functions.compose = function(fn, var_args) {
  var functions = arguments, length = functions.length;
  return function() {
    var self = this, result;
    length && (result = functions[length - 1].apply(self, arguments));
    for (var i = length - 2; 0 <= i; i--) {
      result = functions[i].call(self, result);
    }
    return result;
  };
};
goog.functions.sequence = function(var_args) {
  var functions = arguments, length = functions.length;
  return function() {
    for (var self = this, result, i = 0; i < length; i++) {
      result = functions[i].apply(self, arguments);
    }
    return result;
  };
};
goog.functions.and = function(var_args) {
  var functions = arguments, length = functions.length;
  return function() {
    for (var self = this, i = 0; i < length; i++) {
      if (!functions[i].apply(self, arguments)) {
        return !1;
      }
    }
    return !0;
  };
};
goog.functions.or = function(var_args) {
  var functions = arguments, length = functions.length;
  return function() {
    for (var self = this, i = 0; i < length; i++) {
      if (functions[i].apply(self, arguments)) {
        return !0;
      }
    }
    return !1;
  };
};
goog.functions.not = function(f) {
  return function() {
    var self = this;
    return !f.apply(self, arguments);
  };
};
goog.functions.create = function(constructor, var_args) {
  var temp = function() {
  };
  temp.prototype = constructor.prototype;
  var obj = new temp();
  constructor.apply(obj, Array.prototype.slice.call(arguments, 1));
  return obj;
};
goog.functions.CACHE_RETURN_VALUE = !0;
goog.functions.cacheReturnValue = function(fn) {
  var called = !1, value;
  return function() {
    if (!goog.functions.CACHE_RETURN_VALUE) {
      return fn();
    }
    called || (value = fn(), called = !0);
    return value;
  };
};
goog.functions.once = function(f) {
  var inner = f;
  return function() {
    if (inner) {
      var tmp = inner;
      inner = null;
      tmp();
    }
  };
};
goog.functions.debounce = function(f, interval, opt_scope) {
  var timeout = 0;
  return function(var_args) {
    goog.global.clearTimeout(timeout);
    var args = arguments;
    timeout = goog.global.setTimeout(function() {
      f.apply(opt_scope, args);
    }, interval);
  };
};
goog.functions.throttle = function(f, interval, opt_scope) {
  var timeout = 0, shouldFire = !1, storedArgs = [], handleTimeout = function() {
    timeout = 0;
    shouldFire && (shouldFire = !1, fire());
  }, fire = function() {
    timeout = goog.global.setTimeout(handleTimeout, interval);
    var args = storedArgs;
    storedArgs = [];
    f.apply(opt_scope, args);
  };
  return function(var_args) {
    storedArgs = arguments;
    timeout ? shouldFire = !0 : fire();
  };
};
goog.functions.rateLimit = function(f, interval, opt_scope) {
  var timeout = 0, handleTimeout = function() {
    timeout = 0;
  };
  return function(var_args) {
    timeout || (timeout = goog.global.setTimeout(handleTimeout, interval), f.apply(opt_scope, arguments));
  };
};
goog.functions.isFunction = function(val) {
  return "function" === typeof val;
};
goog.dom.HtmlElement = function() {
};
goog.dom.TagName = function() {
};
goog.dom.TagName.cast = function(name) {
  return name;
};
goog.dom.TagName.prototype.toString = function() {
};
goog.dom.TagName.A = "A";
goog.dom.TagName.ABBR = "ABBR";
goog.dom.TagName.ACRONYM = "ACRONYM";
goog.dom.TagName.ADDRESS = "ADDRESS";
goog.dom.TagName.APPLET = "APPLET";
goog.dom.TagName.AREA = "AREA";
goog.dom.TagName.ARTICLE = "ARTICLE";
goog.dom.TagName.ASIDE = "ASIDE";
goog.dom.TagName.AUDIO = "AUDIO";
goog.dom.TagName.B = "B";
goog.dom.TagName.BASE = "BASE";
goog.dom.TagName.BASEFONT = "BASEFONT";
goog.dom.TagName.BDI = "BDI";
goog.dom.TagName.BDO = "BDO";
goog.dom.TagName.BIG = "BIG";
goog.dom.TagName.BLOCKQUOTE = "BLOCKQUOTE";
goog.dom.TagName.BODY = "BODY";
goog.dom.TagName.BR = "BR";
goog.dom.TagName.BUTTON = "BUTTON";
goog.dom.TagName.CANVAS = "CANVAS";
goog.dom.TagName.CAPTION = "CAPTION";
goog.dom.TagName.CENTER = "CENTER";
goog.dom.TagName.CITE = "CITE";
goog.dom.TagName.CODE = "CODE";
goog.dom.TagName.COL = "COL";
goog.dom.TagName.COLGROUP = "COLGROUP";
goog.dom.TagName.COMMAND = "COMMAND";
goog.dom.TagName.DATA = "DATA";
goog.dom.TagName.DATALIST = "DATALIST";
goog.dom.TagName.DD = "DD";
goog.dom.TagName.DEL = "DEL";
goog.dom.TagName.DETAILS = "DETAILS";
goog.dom.TagName.DFN = "DFN";
goog.dom.TagName.DIALOG = "DIALOG";
goog.dom.TagName.DIR = "DIR";
goog.dom.TagName.DIV = "DIV";
goog.dom.TagName.DL = "DL";
goog.dom.TagName.DT = "DT";
goog.dom.TagName.EM = "EM";
goog.dom.TagName.EMBED = "EMBED";
goog.dom.TagName.FIELDSET = "FIELDSET";
goog.dom.TagName.FIGCAPTION = "FIGCAPTION";
goog.dom.TagName.FIGURE = "FIGURE";
goog.dom.TagName.FONT = "FONT";
goog.dom.TagName.FOOTER = "FOOTER";
goog.dom.TagName.FORM = "FORM";
goog.dom.TagName.FRAME = "FRAME";
goog.dom.TagName.FRAMESET = "FRAMESET";
goog.dom.TagName.H1 = "H1";
goog.dom.TagName.H2 = "H2";
goog.dom.TagName.H3 = "H3";
goog.dom.TagName.H4 = "H4";
goog.dom.TagName.H5 = "H5";
goog.dom.TagName.H6 = "H6";
goog.dom.TagName.HEAD = "HEAD";
goog.dom.TagName.HEADER = "HEADER";
goog.dom.TagName.HGROUP = "HGROUP";
goog.dom.TagName.HR = "HR";
goog.dom.TagName.HTML = "HTML";
goog.dom.TagName.I = "I";
goog.dom.TagName.IFRAME = "IFRAME";
goog.dom.TagName.IMG = "IMG";
goog.dom.TagName.INPUT = "INPUT";
goog.dom.TagName.INS = "INS";
goog.dom.TagName.ISINDEX = "ISINDEX";
goog.dom.TagName.KBD = "KBD";
goog.dom.TagName.KEYGEN = "KEYGEN";
goog.dom.TagName.LABEL = "LABEL";
goog.dom.TagName.LEGEND = "LEGEND";
goog.dom.TagName.LI = "LI";
goog.dom.TagName.LINK = "LINK";
goog.dom.TagName.MAIN = "MAIN";
goog.dom.TagName.MAP = "MAP";
goog.dom.TagName.MARK = "MARK";
goog.dom.TagName.MATH = "MATH";
goog.dom.TagName.MENU = "MENU";
goog.dom.TagName.MENUITEM = "MENUITEM";
goog.dom.TagName.META = "META";
goog.dom.TagName.METER = "METER";
goog.dom.TagName.NAV = "NAV";
goog.dom.TagName.NOFRAMES = "NOFRAMES";
goog.dom.TagName.NOSCRIPT = "NOSCRIPT";
goog.dom.TagName.OBJECT = "OBJECT";
goog.dom.TagName.OL = "OL";
goog.dom.TagName.OPTGROUP = "OPTGROUP";
goog.dom.TagName.OPTION = "OPTION";
goog.dom.TagName.OUTPUT = "OUTPUT";
goog.dom.TagName.P = "P";
goog.dom.TagName.PARAM = "PARAM";
goog.dom.TagName.PICTURE = "PICTURE";
goog.dom.TagName.PRE = "PRE";
goog.dom.TagName.PROGRESS = "PROGRESS";
goog.dom.TagName.Q = "Q";
goog.dom.TagName.RP = "RP";
goog.dom.TagName.RT = "RT";
goog.dom.TagName.RTC = "RTC";
goog.dom.TagName.RUBY = "RUBY";
goog.dom.TagName.S = "S";
goog.dom.TagName.SAMP = "SAMP";
goog.dom.TagName.SCRIPT = "SCRIPT";
goog.dom.TagName.SECTION = "SECTION";
goog.dom.TagName.SELECT = "SELECT";
goog.dom.TagName.SMALL = "SMALL";
goog.dom.TagName.SOURCE = "SOURCE";
goog.dom.TagName.SPAN = "SPAN";
goog.dom.TagName.STRIKE = "STRIKE";
goog.dom.TagName.STRONG = "STRONG";
goog.dom.TagName.STYLE = "STYLE";
goog.dom.TagName.SUB = "SUB";
goog.dom.TagName.SUMMARY = "SUMMARY";
goog.dom.TagName.SUP = "SUP";
goog.dom.TagName.SVG = "SVG";
goog.dom.TagName.TABLE = "TABLE";
goog.dom.TagName.TBODY = "TBODY";
goog.dom.TagName.TD = "TD";
goog.dom.TagName.TEMPLATE = "TEMPLATE";
goog.dom.TagName.TEXTAREA = "TEXTAREA";
goog.dom.TagName.TFOOT = "TFOOT";
goog.dom.TagName.TH = "TH";
goog.dom.TagName.THEAD = "THEAD";
goog.dom.TagName.TIME = "TIME";
goog.dom.TagName.TITLE = "TITLE";
goog.dom.TagName.TR = "TR";
goog.dom.TagName.TRACK = "TRACK";
goog.dom.TagName.TT = "TT";
goog.dom.TagName.U = "U";
goog.dom.TagName.UL = "UL";
goog.dom.TagName.VAR = "VAR";
goog.dom.TagName.VIDEO = "VIDEO";
goog.dom.TagName.WBR = "WBR";
goog.object = {};
function module$contents$goog$object_forEach(obj, f, opt_obj) {
  for (var key in obj) {
    f.call(opt_obj, obj[key], key, obj);
  }
}
function module$contents$goog$object_filter(obj, f, opt_obj) {
  var res = {}, key;
  for (key in obj) {
    f.call(opt_obj, obj[key], key, obj) && (res[key] = obj[key]);
  }
  return res;
}
function module$contents$goog$object_map(obj, f, opt_obj) {
  var res = {}, key;
  for (key in obj) {
    res[key] = f.call(opt_obj, obj[key], key, obj);
  }
  return res;
}
function module$contents$goog$object_some(obj, f, opt_obj) {
  for (var key in obj) {
    if (f.call(opt_obj, obj[key], key, obj)) {
      return !0;
    }
  }
  return !1;
}
function module$contents$goog$object_every(obj, f, opt_obj) {
  for (var key in obj) {
    if (!f.call(opt_obj, obj[key], key, obj)) {
      return !1;
    }
  }
  return !0;
}
function module$contents$goog$object_getCount(obj) {
  var rv = 0, key;
  for (key in obj) {
    rv++;
  }
  return rv;
}
function module$contents$goog$object_getAnyKey(obj) {
  for (var key in obj) {
    return key;
  }
}
function module$contents$goog$object_getAnyValue(obj) {
  for (var key in obj) {
    return obj[key];
  }
}
function module$contents$goog$object_contains(obj, val) {
  return module$contents$goog$object_containsValue(obj, val);
}
function module$contents$goog$object_getValues(obj) {
  var res = [], i = 0, key;
  for (key in obj) {
    res[i++] = obj[key];
  }
  return res;
}
function module$contents$goog$object_getKeys(obj) {
  var res = [], i = 0, key;
  for (key in obj) {
    res[i++] = key;
  }
  return res;
}
function module$contents$goog$object_getValueByKeys(obj, var_args) {
  for (var isArrayLike = goog.isArrayLike(var_args), keys = isArrayLike ? var_args : arguments, i = isArrayLike ? 0 : 1; i < keys.length; i++) {
    if (null == obj) {
      return;
    }
    obj = obj[keys[i]];
  }
  return obj;
}
function module$contents$goog$object_containsKey(obj, key) {
  return null !== obj && key in obj;
}
function module$contents$goog$object_containsValue(obj, val) {
  for (var key in obj) {
    if (obj[key] == val) {
      return !0;
    }
  }
  return !1;
}
function module$contents$goog$object_findKey(obj, f, thisObj) {
  for (var key in obj) {
    if (f.call(thisObj, obj[key], key, obj)) {
      return key;
    }
  }
}
function module$contents$goog$object_findValue(obj, f, thisObj) {
  var key = module$contents$goog$object_findKey(obj, f, thisObj);
  return key && obj[key];
}
function module$contents$goog$object_isEmpty(obj) {
  for (var key in obj) {
    return !1;
  }
  return !0;
}
function module$contents$goog$object_clear(obj) {
  for (var i in obj) {
    delete obj[i];
  }
}
function module$contents$goog$object_remove(obj, key) {
  var rv;
  (rv = key in obj) && delete obj[key];
  return rv;
}
function module$contents$goog$object_add(obj, key, val) {
  if (null !== obj && key in obj) {
    throw Error('The object already contains the key "' + key + '"');
  }
  obj[key] = val;
}
function module$contents$goog$object_get(obj, key, val) {
  return null !== obj && key in obj ? obj[key] : val;
}
function module$contents$goog$object_set(obj, key, value) {
  obj[key] = value;
}
function module$contents$goog$object_setIfUndefined(obj, key, value) {
  return key in obj ? obj[key] : obj[key] = value;
}
function module$contents$goog$object_setWithReturnValueIfNotSet(obj, key, f) {
  if (key in obj) {
    return obj[key];
  }
  var val = f();
  return obj[key] = val;
}
function module$contents$goog$object_equals(a, b) {
  for (var k in a) {
    if (!(k in b) || a[k] !== b[k]) {
      return !1;
    }
  }
  for (var k$15 in b) {
    if (!(k$15 in a)) {
      return !1;
    }
  }
  return !0;
}
function module$contents$goog$object_clone(obj) {
  var res = {}, key;
  for (key in obj) {
    res[key] = obj[key];
  }
  return res;
}
function module$contents$goog$object_unsafeClone(obj) {
  if (!obj || "object" !== typeof obj) {
    return obj;
  }
  if ("function" === typeof obj.clone) {
    return obj.clone();
  }
  if ("undefined" !== typeof Map && obj instanceof Map) {
    return new Map(obj);
  }
  if ("undefined" !== typeof Set && obj instanceof Set) {
    return new Set(obj);
  }
  var clone = Array.isArray(obj) ? [] : "function" !== typeof ArrayBuffer || "function" !== typeof ArrayBuffer.isView || !ArrayBuffer.isView(obj) || obj instanceof DataView ? {} : new obj.constructor(obj.length), key;
  for (key in obj) {
    clone[key] = module$contents$goog$object_unsafeClone(obj[key]);
  }
  return clone;
}
function module$contents$goog$object_transpose(obj) {
  var transposed = {}, key;
  for (key in obj) {
    transposed[obj[key]] = key;
  }
  return transposed;
}
var module$contents$goog$object_PROTOTYPE_FIELDS = "constructor hasOwnProperty isPrototypeOf propertyIsEnumerable toLocaleString toString valueOf".split(" ");
function module$contents$goog$object_extend(target, var_args) {
  for (var key, source, i = 1; i < arguments.length; i++) {
    source = arguments[i];
    for (key in source) {
      target[key] = source[key];
    }
    for (var j = 0; j < module$contents$goog$object_PROTOTYPE_FIELDS.length; j++) {
      key = module$contents$goog$object_PROTOTYPE_FIELDS[j], Object.prototype.hasOwnProperty.call(source, key) && (target[key] = source[key]);
    }
  }
}
function module$contents$goog$object_create(var_args) {
  var argLength = arguments.length;
  if (1 == argLength && Array.isArray(arguments[0])) {
    return module$contents$goog$object_create.apply(null, arguments[0]);
  }
  if (argLength % 2) {
    throw Error("Uneven number of arguments");
  }
  for (var rv = {}, i = 0; i < argLength; i += 2) {
    rv[arguments[i]] = arguments[i + 1];
  }
  return rv;
}
function module$contents$goog$object_createSet(var_args) {
  var argLength = arguments.length;
  if (1 == argLength && Array.isArray(arguments[0])) {
    return module$contents$goog$object_createSet.apply(null, arguments[0]);
  }
  for (var rv = {}, i = 0; i < argLength; i++) {
    rv[arguments[i]] = !0;
  }
  return rv;
}
function module$contents$goog$object_createImmutableView(obj) {
  var result = obj;
  Object.isFrozen && !Object.isFrozen(obj) && (result = Object.create(obj), Object.freeze(result));
  return result;
}
function module$contents$goog$object_isImmutableView(obj) {
  return !!Object.isFrozen && Object.isFrozen(obj);
}
function module$contents$goog$object_getAllPropertyNames(obj, includeObjectPrototype, includeFunctionPrototype) {
  if (!obj) {
    return [];
  }
  if (!Object.getOwnPropertyNames || !Object.getPrototypeOf) {
    return module$contents$goog$object_getKeys(obj);
  }
  for (var visitedSet = {}, proto = obj; proto && (proto !== Object.prototype || includeObjectPrototype) && (proto !== Function.prototype || includeFunctionPrototype);) {
    for (var names = Object.getOwnPropertyNames(proto), i = 0; i < names.length; i++) {
      visitedSet[names[i]] = !0;
    }
    proto = Object.getPrototypeOf(proto);
  }
  return module$contents$goog$object_getKeys(visitedSet);
}
function module$contents$goog$object_getSuperClass(constructor) {
  var proto = Object.getPrototypeOf(constructor.prototype);
  return proto && proto.constructor;
}
goog.object.add = module$contents$goog$object_add;
goog.object.clear = module$contents$goog$object_clear;
goog.object.clone = module$contents$goog$object_clone;
goog.object.contains = module$contents$goog$object_contains;
goog.object.containsKey = module$contents$goog$object_containsKey;
goog.object.containsValue = module$contents$goog$object_containsValue;
goog.object.create = module$contents$goog$object_create;
goog.object.createImmutableView = module$contents$goog$object_createImmutableView;
goog.object.createSet = module$contents$goog$object_createSet;
goog.object.equals = module$contents$goog$object_equals;
goog.object.every = module$contents$goog$object_every;
goog.object.extend = module$contents$goog$object_extend;
goog.object.filter = module$contents$goog$object_filter;
goog.object.findKey = module$contents$goog$object_findKey;
goog.object.findValue = module$contents$goog$object_findValue;
goog.object.forEach = module$contents$goog$object_forEach;
goog.object.get = module$contents$goog$object_get;
goog.object.getAllPropertyNames = module$contents$goog$object_getAllPropertyNames;
goog.object.getAnyKey = module$contents$goog$object_getAnyKey;
goog.object.getAnyValue = module$contents$goog$object_getAnyValue;
goog.object.getCount = module$contents$goog$object_getCount;
goog.object.getKeys = module$contents$goog$object_getKeys;
goog.object.getSuperClass = module$contents$goog$object_getSuperClass;
goog.object.getValueByKeys = module$contents$goog$object_getValueByKeys;
goog.object.getValues = module$contents$goog$object_getValues;
goog.object.isEmpty = module$contents$goog$object_isEmpty;
goog.object.isImmutableView = module$contents$goog$object_isImmutableView;
goog.object.map = module$contents$goog$object_map;
goog.object.remove = module$contents$goog$object_remove;
goog.object.set = module$contents$goog$object_set;
goog.object.setIfUndefined = module$contents$goog$object_setIfUndefined;
goog.object.setWithReturnValueIfNotSet = module$contents$goog$object_setWithReturnValueIfNotSet;
goog.object.some = module$contents$goog$object_some;
goog.object.transpose = module$contents$goog$object_transpose;
goog.object.unsafeClone = module$contents$goog$object_unsafeClone;
goog.dom.tags = {};
goog.dom.tags.VOID_TAGS_ = {area:!0, base:!0, br:!0, col:!0, command:!0, embed:!0, hr:!0, img:!0, input:!0, keygen:!0, link:!0, meta:!0, param:!0, source:!0, track:!0, wbr:!0};
goog.dom.tags.isVoidTag = function(tagName) {
  return !0 === goog.dom.tags.VOID_TAGS_[tagName];
};
goog.html = {};
goog.html.trustedtypes = {};
goog.html.trustedtypes.POLICY_NAME = goog.TRUSTED_TYPES_POLICY_NAME ? goog.TRUSTED_TYPES_POLICY_NAME + "#html" : "";
goog.html.trustedtypes.getPolicyPrivateDoNotAccessOrElse = function() {
  if (!goog.html.trustedtypes.POLICY_NAME) {
    return null;
  }
  void 0 === goog.html.trustedtypes.cachedPolicy_ && (goog.html.trustedtypes.cachedPolicy_ = goog.createTrustedTypesPolicy(goog.html.trustedtypes.POLICY_NAME));
  return goog.html.trustedtypes.cachedPolicy_;
};
goog.string.TypedString = function() {
};
goog.string.Const = function(opt_token, opt_content) {
  this.stringConstValueWithSecurityContract__googStringSecurityPrivate_ = opt_token === goog.string.Const.GOOG_STRING_CONSTRUCTOR_TOKEN_PRIVATE_ && opt_content || "";
  this.STRING_CONST_TYPE_MARKER__GOOG_STRING_SECURITY_PRIVATE_ = goog.string.Const.TYPE_MARKER_;
};
goog.string.Const.prototype.implementsGoogStringTypedString = !0;
goog.string.Const.prototype.getTypedStringValue = function() {
  return this.stringConstValueWithSecurityContract__googStringSecurityPrivate_;
};
goog.DEBUG && (goog.string.Const.prototype.toString = function() {
  return "Const{" + this.stringConstValueWithSecurityContract__googStringSecurityPrivate_ + "}";
});
goog.string.Const.unwrap = function(stringConst) {
  if (stringConst instanceof goog.string.Const && stringConst.constructor === goog.string.Const && stringConst.STRING_CONST_TYPE_MARKER__GOOG_STRING_SECURITY_PRIVATE_ === goog.string.Const.TYPE_MARKER_) {
    return stringConst.stringConstValueWithSecurityContract__googStringSecurityPrivate_;
  }
  goog.asserts.fail("expected object of type Const, got '" + stringConst + "'");
  return "type_error:Const";
};
goog.string.Const.from = function(s) {
  return new goog.string.Const(goog.string.Const.GOOG_STRING_CONSTRUCTOR_TOKEN_PRIVATE_, s);
};
goog.string.Const.TYPE_MARKER_ = {};
goog.string.Const.GOOG_STRING_CONSTRUCTOR_TOKEN_PRIVATE_ = {};
goog.string.Const.EMPTY = goog.string.Const.from("");
var module$contents$goog$html$SafeScript_CONSTRUCTOR_TOKEN_PRIVATE = {}, module$contents$goog$html$SafeScript_SafeScript = function(value, token) {
  this.privateDoNotAccessOrElseSafeScriptWrappedValue_ = token === module$contents$goog$html$SafeScript_CONSTRUCTOR_TOKEN_PRIVATE ? value : "";
  this.implementsGoogStringTypedString = !0;
};
module$contents$goog$html$SafeScript_SafeScript.prototype.toString = function() {
  return this.privateDoNotAccessOrElseSafeScriptWrappedValue_.toString();
};
module$contents$goog$html$SafeScript_SafeScript.fromConstant = function(script) {
  var scriptString = goog.string.Const.unwrap(script);
  return 0 === scriptString.length ? module$contents$goog$html$SafeScript_SafeScript.EMPTY : module$contents$goog$html$SafeScript_SafeScript.createSafeScriptSecurityPrivateDoNotAccessOrElse(scriptString);
};
module$contents$goog$html$SafeScript_SafeScript.prototype.getTypedStringValue = function() {
  return this.privateDoNotAccessOrElseSafeScriptWrappedValue_.toString();
};
module$contents$goog$html$SafeScript_SafeScript.unwrap = function(safeScript) {
  return module$contents$goog$html$SafeScript_SafeScript.unwrapTrustedScript(safeScript).toString();
};
module$contents$goog$html$SafeScript_SafeScript.unwrapTrustedScript = function(safeScript) {
  if (safeScript instanceof module$contents$goog$html$SafeScript_SafeScript && safeScript.constructor === module$contents$goog$html$SafeScript_SafeScript) {
    return safeScript.privateDoNotAccessOrElseSafeScriptWrappedValue_;
  }
  (0,goog.asserts.fail)("expected object of type SafeScript, got '" + safeScript + "' of type " + goog.typeOf(safeScript));
  return "type_error:SafeScript";
};
module$contents$goog$html$SafeScript_SafeScript.createSafeScriptSecurityPrivateDoNotAccessOrElse = function(script) {
  var noinlineScript = script, policy = goog.html.trustedtypes.getPolicyPrivateDoNotAccessOrElse(), trustedScript = policy ? policy.createScript(noinlineScript) : noinlineScript;
  return new module$contents$goog$html$SafeScript_SafeScript(trustedScript, module$contents$goog$html$SafeScript_CONSTRUCTOR_TOKEN_PRIVATE);
};
module$contents$goog$html$SafeScript_SafeScript.EMPTY = module$contents$goog$html$SafeScript_SafeScript.createSafeScriptSecurityPrivateDoNotAccessOrElse("");
goog.html.SafeScript = module$contents$goog$html$SafeScript_SafeScript;
goog.fs = {};
goog.fs.url = {};
goog.fs.url.createObjectUrl = function(obj) {
  return goog.fs.url.getUrlObject_().createObjectURL(obj);
};
goog.fs.url.revokeObjectUrl = function(url) {
  goog.fs.url.getUrlObject_().revokeObjectURL(url);
};
goog.fs.url.UrlObject_ = function() {
};
goog.fs.url.UrlObject_.prototype.createObjectURL = function() {
};
goog.fs.url.UrlObject_.prototype.revokeObjectURL = function() {
};
goog.fs.url.getUrlObject_ = function() {
  var urlObject = goog.fs.url.findUrlObject_();
  if (null != urlObject) {
    return urlObject;
  }
  throw Error("This browser doesn't seem to support blob URLs");
};
goog.fs.url.findUrlObject_ = function() {
  return void 0 !== goog.global.URL && void 0 !== goog.global.URL.createObjectURL ? goog.global.URL : void 0 !== goog.global.createObjectURL ? goog.global : null;
};
goog.fs.url.browserSupportsObjectUrls = function() {
  return null != goog.fs.url.findUrlObject_();
};
goog.fs.blob = {};
goog.fs.blob.getBlob = function(var_args) {
  var BlobBuilder = goog.global.BlobBuilder || goog.global.WebKitBlobBuilder;
  if (void 0 !== BlobBuilder) {
    for (var bb = new BlobBuilder(), i = 0; i < arguments.length; i++) {
      bb.append(arguments[i]);
    }
    return bb.getBlob();
  }
  return goog.fs.blob.getBlobWithProperties(Array.prototype.slice.call(arguments));
};
goog.fs.blob.getBlobWithProperties = function(parts, opt_type, opt_endings) {
  var BlobBuilder = goog.global.BlobBuilder || goog.global.WebKitBlobBuilder;
  if (void 0 !== BlobBuilder) {
    for (var bb = new BlobBuilder(), i = 0; i < parts.length; i++) {
      bb.append(parts[i], opt_endings);
    }
    return bb.getBlob(opt_type);
  }
  if (void 0 !== goog.global.Blob) {
    var properties = {};
    opt_type && (properties.type = opt_type);
    opt_endings && (properties.endings = opt_endings);
    return new Blob(parts, properties);
  }
  throw Error("This browser doesn't seem to support creating Blobs");
};
goog.html.TrustedResourceUrl = function(value, token) {
  this.privateDoNotAccessOrElseTrustedResourceUrlWrappedValue_ = token === goog.html.TrustedResourceUrl.CONSTRUCTOR_TOKEN_PRIVATE_ ? value : "";
};
goog.html.TrustedResourceUrl.prototype.toString = function() {
  return this.privateDoNotAccessOrElseTrustedResourceUrlWrappedValue_ + "";
};
goog.html.TrustedResourceUrl.prototype.implementsGoogStringTypedString = !0;
goog.html.TrustedResourceUrl.prototype.getTypedStringValue = function() {
  return this.privateDoNotAccessOrElseTrustedResourceUrlWrappedValue_.toString();
};
goog.html.TrustedResourceUrl.prototype.cloneWithParams = function(searchParams, opt_hashParams) {
  var url = goog.html.TrustedResourceUrl.unwrap(this), parts = goog.html.TrustedResourceUrl.URL_PARAM_PARSER_.exec(url), urlBase = parts[1], urlSearch = parts[2] || "", urlHash = parts[3] || "";
  return goog.html.TrustedResourceUrl.createTrustedResourceUrlSecurityPrivateDoNotAccessOrElse(urlBase + goog.html.TrustedResourceUrl.stringifyParams_("?", urlSearch, searchParams) + goog.html.TrustedResourceUrl.stringifyParams_("#", urlHash, opt_hashParams));
};
goog.html.TrustedResourceUrl.unwrap = function(trustedResourceUrl) {
  return goog.html.TrustedResourceUrl.unwrapTrustedScriptURL(trustedResourceUrl).toString();
};
goog.html.TrustedResourceUrl.unwrapTrustedScriptURL = function(trustedResourceUrl) {
  if (trustedResourceUrl instanceof goog.html.TrustedResourceUrl && trustedResourceUrl.constructor === goog.html.TrustedResourceUrl) {
    return trustedResourceUrl.privateDoNotAccessOrElseTrustedResourceUrlWrappedValue_;
  }
  goog.asserts.fail("expected object of type TrustedResourceUrl, got '" + trustedResourceUrl + "' of type " + goog.typeOf(trustedResourceUrl));
  return "type_error:TrustedResourceUrl";
};
goog.html.TrustedResourceUrl.format = function(format, args) {
  var formatStr = goog.string.Const.unwrap(format);
  if (!goog.html.TrustedResourceUrl.BASE_URL_.test(formatStr)) {
    throw Error("Invalid TrustedResourceUrl format: " + formatStr);
  }
  var result = formatStr.replace(goog.html.TrustedResourceUrl.FORMAT_MARKER_, function(match, id) {
    if (!Object.prototype.hasOwnProperty.call(args, id)) {
      throw Error('Found marker, "' + id + '", in format string, "' + formatStr + '", but no valid label mapping found in args: ' + JSON.stringify(args));
    }
    var arg = args[id];
    return arg instanceof goog.string.Const ? goog.string.Const.unwrap(arg) : encodeURIComponent(String(arg));
  });
  return goog.html.TrustedResourceUrl.createTrustedResourceUrlSecurityPrivateDoNotAccessOrElse(result);
};
goog.html.TrustedResourceUrl.FORMAT_MARKER_ = /%{(\w+)}/g;
goog.html.TrustedResourceUrl.BASE_URL_ = RegExp("^((https:)?//[0-9a-z.:[\\]-]+/|/[^/\\\\]|[^:/\\\\%]+/|[^:/\\\\%]*[?#]|about:blank#)", "i");
goog.html.TrustedResourceUrl.URL_PARAM_PARSER_ = /^([^?#]*)(\?[^#]*)?(#[\s\S]*)?/;
goog.html.TrustedResourceUrl.formatWithParams = function(format, args, searchParams, opt_hashParams) {
  var url = goog.html.TrustedResourceUrl.format(format, args);
  return url.cloneWithParams(searchParams, opt_hashParams);
};
goog.html.TrustedResourceUrl.fromConstant = function(url) {
  return goog.html.TrustedResourceUrl.createTrustedResourceUrlSecurityPrivateDoNotAccessOrElse(goog.string.Const.unwrap(url));
};
goog.html.TrustedResourceUrl.fromConstants = function(parts) {
  for (var unwrapped = "", i = 0; i < parts.length; i++) {
    unwrapped += goog.string.Const.unwrap(parts[i]);
  }
  return goog.html.TrustedResourceUrl.createTrustedResourceUrlSecurityPrivateDoNotAccessOrElse(unwrapped);
};
goog.html.TrustedResourceUrl.fromSafeScript = function(safeScript) {
  var blob = goog.fs.blob.getBlobWithProperties([module$contents$goog$html$SafeScript_SafeScript.unwrap(safeScript)], "text/javascript"), url = goog.fs.url.createObjectUrl(blob);
  return goog.html.TrustedResourceUrl.createTrustedResourceUrlSecurityPrivateDoNotAccessOrElse(url);
};
goog.html.TrustedResourceUrl.CONSTRUCTOR_TOKEN_PRIVATE_ = {};
goog.html.TrustedResourceUrl.createTrustedResourceUrlSecurityPrivateDoNotAccessOrElse = function(url) {
  var noinlineUrl = url, policy = goog.html.trustedtypes.getPolicyPrivateDoNotAccessOrElse(), value = policy ? policy.createScriptURL(noinlineUrl) : noinlineUrl;
  return new goog.html.TrustedResourceUrl(value, goog.html.TrustedResourceUrl.CONSTRUCTOR_TOKEN_PRIVATE_);
};
goog.html.TrustedResourceUrl.stringifyParams_ = function(prefix, currentString, params) {
  if (null == params) {
    return currentString;
  }
  if ("string" === typeof params) {
    return params ? prefix + encodeURIComponent(params) : "";
  }
  for (var key in params) {
    if (Object.prototype.hasOwnProperty.call(params, key)) {
      for (var value = params[key], outputValues = Array.isArray(value) ? value : [value], i = 0; i < outputValues.length; i++) {
        var outputValue = outputValues[i];
        null != outputValue && (currentString || (currentString = prefix), currentString += (currentString.length > prefix.length ? "&" : "") + encodeURIComponent(key) + "=" + encodeURIComponent(String(outputValue)));
      }
    }
  }
  return currentString;
};
goog.html.SafeUrl = function(value, token) {
  this.privateDoNotAccessOrElseSafeUrlWrappedValue_ = token === goog.html.SafeUrl.CONSTRUCTOR_TOKEN_PRIVATE_ ? value : "";
};
goog.html.SafeUrl.prototype.toString = function() {
  return this.privateDoNotAccessOrElseSafeUrlWrappedValue_.toString();
};
goog.html.SafeUrl.INNOCUOUS_STRING = "about:invalid#zClosurez";
goog.html.SafeUrl.prototype.implementsGoogStringTypedString = !0;
goog.html.SafeUrl.prototype.getTypedStringValue = function() {
  return this.privateDoNotAccessOrElseSafeUrlWrappedValue_.toString();
};
goog.html.SafeUrl.unwrap = function(safeUrl) {
  if (safeUrl instanceof goog.html.SafeUrl && safeUrl.constructor === goog.html.SafeUrl) {
    return safeUrl.privateDoNotAccessOrElseSafeUrlWrappedValue_;
  }
  goog.asserts.fail("expected object of type SafeUrl, got '" + safeUrl + "' of type " + goog.typeOf(safeUrl));
  return "type_error:SafeUrl";
};
goog.html.SafeUrl.fromConstant = function(url) {
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(goog.string.Const.unwrap(url));
};
goog.html.SAFE_MIME_TYPE_PATTERN_ = RegExp('^(?:audio/(?:3gpp2|3gpp|aac|L16|midi|mp3|mp4|mpeg|oga|ogg|opus|x-m4a|x-matroska|x-wav|wav|webm)|font/\\w+|image/(?:bmp|gif|jpeg|jpg|png|tiff|webp|x-icon|heic|heif)|video/(?:mpeg|mp4|ogg|webm|quicktime|x-matroska))(?:;\\w+=(?:\\w+|"[\\w;,= ]+"))*$', "i");
goog.html.SafeUrl.isSafeMimeType = function(mimeType) {
  return goog.html.SAFE_MIME_TYPE_PATTERN_.test(mimeType);
};
goog.html.SafeUrl.fromBlob = function(blob) {
  var url = goog.html.SafeUrl.isSafeMimeType(blob.type) ? goog.fs.url.createObjectUrl(blob) : goog.html.SafeUrl.INNOCUOUS_STRING;
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(url);
};
goog.html.SafeUrl.revokeObjectUrl = function(safeUrl) {
  var url = safeUrl.getTypedStringValue();
  url !== goog.html.SafeUrl.INNOCUOUS_STRING && goog.fs.url.revokeObjectUrl(url);
};
goog.html.SafeUrl.fromMediaSource = function(mediaSource) {
  goog.asserts.assert("MediaSource" in goog.global, "No support for MediaSource");
  var url = mediaSource instanceof MediaSource ? goog.fs.url.createObjectUrl(mediaSource) : goog.html.SafeUrl.INNOCUOUS_STRING;
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(url);
};
goog.html.DATA_URL_PATTERN_ = /^data:(.*);base64,[a-z0-9+\/]+=*$/i;
goog.html.SafeUrl.tryFromDataUrl = function(dataUrl) {
  dataUrl = String(dataUrl);
  var filteredDataUrl = dataUrl.replace(/(%0A|%0D)/g, ""), match = filteredDataUrl.match(goog.html.DATA_URL_PATTERN_);
  return match ? goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(filteredDataUrl) : null;
};
goog.html.SafeUrl.fromDataUrl = function(dataUrl) {
  return goog.html.SafeUrl.tryFromDataUrl(dataUrl) || goog.html.SafeUrl.INNOCUOUS_URL;
};
goog.html.SafeUrl.fromTelUrl = function(telUrl) {
  goog.string.internal.caseInsensitiveStartsWith(telUrl, "tel:") || (telUrl = goog.html.SafeUrl.INNOCUOUS_STRING);
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(telUrl);
};
goog.html.SIP_URL_PATTERN_ = RegExp("^sip[s]?:[+a-z0-9_.!$%&'*\\/=^`{|}~-]+@([a-z0-9-]+\\.)+[a-z0-9]{2,63}$", "i");
goog.html.SafeUrl.fromSipUrl = function(sipUrl) {
  goog.html.SIP_URL_PATTERN_.test(decodeURIComponent(sipUrl)) || (sipUrl = goog.html.SafeUrl.INNOCUOUS_STRING);
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(sipUrl);
};
goog.html.SafeUrl.fromFacebookMessengerUrl = function(facebookMessengerUrl) {
  goog.string.internal.caseInsensitiveStartsWith(facebookMessengerUrl, "fb-messenger://share") || (facebookMessengerUrl = goog.html.SafeUrl.INNOCUOUS_STRING);
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(facebookMessengerUrl);
};
goog.html.SafeUrl.fromWhatsAppUrl = function(whatsAppUrl) {
  goog.string.internal.caseInsensitiveStartsWith(whatsAppUrl, "whatsapp://send") || (whatsAppUrl = goog.html.SafeUrl.INNOCUOUS_STRING);
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(whatsAppUrl);
};
goog.html.SafeUrl.fromSmsUrl = function(smsUrl) {
  goog.string.internal.caseInsensitiveStartsWith(smsUrl, "sms:") && goog.html.SafeUrl.isSmsUrlBodyValid_(smsUrl) || (smsUrl = goog.html.SafeUrl.INNOCUOUS_STRING);
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(smsUrl);
};
goog.html.SafeUrl.isSmsUrlBodyValid_ = function(smsUrl) {
  var hash = smsUrl.indexOf("#");
  0 < hash && (smsUrl = smsUrl.substring(0, hash));
  var bodyParams = smsUrl.match(/[?&]body=/gi);
  if (!bodyParams) {
    return !0;
  }
  if (1 < bodyParams.length) {
    return !1;
  }
  var bodyValue = smsUrl.match(/[?&]body=([^&]*)/)[1];
  if (!bodyValue) {
    return !0;
  }
  try {
    decodeURIComponent(bodyValue);
  } catch (error) {
    return !1;
  }
  return /^(?:[a-z0-9\-_.~]|%[0-9a-f]{2})+$/i.test(bodyValue);
};
goog.html.SafeUrl.fromSshUrl = function(sshUrl) {
  goog.string.internal.caseInsensitiveStartsWith(sshUrl, "ssh://") || (sshUrl = goog.html.SafeUrl.INNOCUOUS_STRING);
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(sshUrl);
};
goog.html.SafeUrl.sanitizeChromeExtensionUrl = function(url, extensionId) {
  return goog.html.SafeUrl.sanitizeExtensionUrl_(/^chrome-extension:\/\/([^\/]+)\//, url, extensionId);
};
goog.html.SafeUrl.sanitizeFirefoxExtensionUrl = function(url, extensionId) {
  return goog.html.SafeUrl.sanitizeExtensionUrl_(/^moz-extension:\/\/([^\/]+)\//, url, extensionId);
};
goog.html.SafeUrl.sanitizeEdgeExtensionUrl = function(url, extensionId) {
  return goog.html.SafeUrl.sanitizeExtensionUrl_(/^ms-browser-extension:\/\/([^\/]+)\//, url, extensionId);
};
goog.html.SafeUrl.sanitizeExtensionUrl_ = function(scheme, url, extensionId) {
  var matches = scheme.exec(url);
  if (matches) {
    var extractedExtensionId = matches[1];
    var acceptedExtensionIds = extensionId instanceof goog.string.Const ? [goog.string.Const.unwrap(extensionId)] : extensionId.map(function(x) {
      return goog.string.Const.unwrap(x);
    });
    -1 == acceptedExtensionIds.indexOf(extractedExtensionId) && (url = goog.html.SafeUrl.INNOCUOUS_STRING);
  } else {
    url = goog.html.SafeUrl.INNOCUOUS_STRING;
  }
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(url);
};
goog.html.SafeUrl.fromTrustedResourceUrl = function(trustedResourceUrl) {
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(goog.html.TrustedResourceUrl.unwrap(trustedResourceUrl));
};
goog.html.SAFE_URL_PATTERN_ = /^(?:(?:https?|mailto|ftp):|[^:/?#]*(?:[/?#]|$))/i;
goog.html.SafeUrl.SAFE_URL_PATTERN = goog.html.SAFE_URL_PATTERN_;
goog.html.SafeUrl.trySanitize = function(url) {
  if (url instanceof goog.html.SafeUrl) {
    return url;
  }
  url = "object" == typeof url && url.implementsGoogStringTypedString ? url.getTypedStringValue() : String(url);
  return goog.html.SAFE_URL_PATTERN_.test(url) ? goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(url) : goog.html.SafeUrl.tryFromDataUrl(url);
};
goog.html.SafeUrl.sanitize = function(url) {
  return goog.html.SafeUrl.trySanitize(url) || goog.html.SafeUrl.INNOCUOUS_URL;
};
goog.html.SafeUrl.sanitizeAssertUnchanged = function(url, opt_allowDataUrl) {
  if (url instanceof goog.html.SafeUrl) {
    return url;
  }
  url = "object" == typeof url && url.implementsGoogStringTypedString ? url.getTypedStringValue() : String(url);
  if (opt_allowDataUrl && /^data:/i.test(url)) {
    var safeUrl = goog.html.SafeUrl.fromDataUrl(url);
    if (safeUrl.getTypedStringValue() == url) {
      return safeUrl;
    }
  }
  goog.asserts.assert(goog.html.SAFE_URL_PATTERN_.test(url), "%s does not match the safe URL pattern", url) || (url = goog.html.SafeUrl.INNOCUOUS_STRING);
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(url);
};
goog.html.SafeUrl.CONSTRUCTOR_TOKEN_PRIVATE_ = {};
goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse = function(url) {
  return new goog.html.SafeUrl(url, goog.html.SafeUrl.CONSTRUCTOR_TOKEN_PRIVATE_);
};
goog.html.SafeUrl.INNOCUOUS_URL = goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(goog.html.SafeUrl.INNOCUOUS_STRING);
goog.html.SafeUrl.ABOUT_BLANK = goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse("about:blank");
var module$contents$goog$html$SafeStyle_CONSTRUCTOR_TOKEN_PRIVATE = {}, module$contents$goog$html$SafeStyle_SafeStyle = function(value, token) {
  this.privateDoNotAccessOrElseSafeStyleWrappedValue_ = token === module$contents$goog$html$SafeStyle_CONSTRUCTOR_TOKEN_PRIVATE ? value : "";
  this.implementsGoogStringTypedString = !0;
};
module$contents$goog$html$SafeStyle_SafeStyle.fromConstant = function(style) {
  var styleString = goog.string.Const.unwrap(style);
  if (0 === styleString.length) {
    return module$contents$goog$html$SafeStyle_SafeStyle.EMPTY;
  }
  (0,goog.asserts.assert)((0,goog.string.internal.endsWith)(styleString, ";"), "Last character of style string is not ';': " + styleString);
  (0,goog.asserts.assert)((0,goog.string.internal.contains)(styleString, ":"), "Style string must contain at least one ':', to specify a \"name: value\" pair: " + styleString);
  return module$contents$goog$html$SafeStyle_SafeStyle.createSafeStyleSecurityPrivateDoNotAccessOrElse(styleString);
};
module$contents$goog$html$SafeStyle_SafeStyle.prototype.getTypedStringValue = function() {
  return this.privateDoNotAccessOrElseSafeStyleWrappedValue_;
};
module$contents$goog$html$SafeStyle_SafeStyle.prototype.toString = function() {
  return this.privateDoNotAccessOrElseSafeStyleWrappedValue_.toString();
};
module$contents$goog$html$SafeStyle_SafeStyle.unwrap = function(safeStyle) {
  if (safeStyle instanceof module$contents$goog$html$SafeStyle_SafeStyle && safeStyle.constructor === module$contents$goog$html$SafeStyle_SafeStyle) {
    return safeStyle.privateDoNotAccessOrElseSafeStyleWrappedValue_;
  }
  (0,goog.asserts.fail)("expected object of type SafeStyle, got '" + safeStyle + "' of type " + goog.typeOf(safeStyle));
  return "type_error:SafeStyle";
};
module$contents$goog$html$SafeStyle_SafeStyle.createSafeStyleSecurityPrivateDoNotAccessOrElse = function(style) {
  return new module$contents$goog$html$SafeStyle_SafeStyle(style, module$contents$goog$html$SafeStyle_CONSTRUCTOR_TOKEN_PRIVATE);
};
module$contents$goog$html$SafeStyle_SafeStyle.create = function(map) {
  var style = "", name;
  for (name in map) {
    if (Object.prototype.hasOwnProperty.call(map, name)) {
      if (!/^[-_a-zA-Z0-9]+$/.test(name)) {
        throw Error("Name allows only [-_a-zA-Z0-9], got: " + name);
      }
      var value = map[name];
      null != value && (value = Array.isArray(value) ? value.map(module$contents$goog$html$SafeStyle_sanitizePropertyValue).join(" ") : module$contents$goog$html$SafeStyle_sanitizePropertyValue(value), style += name + ":" + value + ";");
    }
  }
  return style ? module$contents$goog$html$SafeStyle_SafeStyle.createSafeStyleSecurityPrivateDoNotAccessOrElse(style) : module$contents$goog$html$SafeStyle_SafeStyle.EMPTY;
};
module$contents$goog$html$SafeStyle_SafeStyle.concat = function(var_args) {
  var style = "", addArgument = function(argument) {
    Array.isArray(argument) ? argument.forEach(addArgument) : style += module$contents$goog$html$SafeStyle_SafeStyle.unwrap(argument);
  };
  Array.prototype.forEach.call(arguments, addArgument);
  return style ? module$contents$goog$html$SafeStyle_SafeStyle.createSafeStyleSecurityPrivateDoNotAccessOrElse(style) : module$contents$goog$html$SafeStyle_SafeStyle.EMPTY;
};
module$contents$goog$html$SafeStyle_SafeStyle.EMPTY = module$contents$goog$html$SafeStyle_SafeStyle.createSafeStyleSecurityPrivateDoNotAccessOrElse("");
module$contents$goog$html$SafeStyle_SafeStyle.INNOCUOUS_STRING = "zClosurez";
function module$contents$goog$html$SafeStyle_sanitizePropertyValue(value) {
  if (value instanceof goog.html.SafeUrl) {
    var url = goog.html.SafeUrl.unwrap(value);
    return 'url("' + url.replace(/</g, "%3c").replace(/[\\"]/g, "\\$&") + '")';
  }
  var result = value instanceof goog.string.Const ? goog.string.Const.unwrap(value) : module$contents$goog$html$SafeStyle_sanitizePropertyValueString(String(value));
  if (/[{;}]/.test(result)) {
    throw new module$contents$goog$asserts_AssertionError("Value does not allow [{;}], got: %s.", [result]);
  }
  return result;
}
function module$contents$goog$html$SafeStyle_sanitizePropertyValueString(value) {
  var valueWithoutFunctions = value.replace(module$contents$goog$html$SafeStyle_FUNCTIONS_RE, "$1").replace(module$contents$goog$html$SafeStyle_FUNCTIONS_RE, "$1").replace(module$contents$goog$html$SafeStyle_URL_RE, "url");
  if (module$contents$goog$html$SafeStyle_VALUE_RE.test(valueWithoutFunctions)) {
    if (module$contents$goog$html$SafeStyle_COMMENT_RE.test(value)) {
      return (0,goog.asserts.fail)("String value disallows comments, got: " + value), module$contents$goog$html$SafeStyle_SafeStyle.INNOCUOUS_STRING;
    }
    for (var JSCompiler_inline_result, outsideSingle = !0, outsideDouble = !0, i = 0; i < value.length; i++) {
      var c = value.charAt(i);
      "'" == c && outsideDouble ? outsideSingle = !outsideSingle : '"' == c && outsideSingle && (outsideDouble = !outsideDouble);
    }
    JSCompiler_inline_result = outsideSingle && outsideDouble;
    if (!JSCompiler_inline_result) {
      return (0,goog.asserts.fail)("String value requires balanced quotes, got: " + value), module$contents$goog$html$SafeStyle_SafeStyle.INNOCUOUS_STRING;
    }
    if (!module$contents$goog$html$SafeStyle_hasBalancedSquareBrackets(value)) {
      return (0,goog.asserts.fail)("String value requires balanced square brackets and one identifier per pair of brackets, got: " + value), module$contents$goog$html$SafeStyle_SafeStyle.INNOCUOUS_STRING;
    }
  } else {
    return (0,goog.asserts.fail)("String value allows only [-,.\"'%_!#/ a-zA-Z0-9\\[\\]] and simple functions, got: " + value), module$contents$goog$html$SafeStyle_SafeStyle.INNOCUOUS_STRING;
  }
  return module$contents$goog$html$SafeStyle_sanitizeUrl(value);
}
function module$contents$goog$html$SafeStyle_hasBalancedSquareBrackets(value) {
  for (var outside = !0, tokenRe = /^[-_a-zA-Z0-9]$/, i = 0; i < value.length; i++) {
    var c = value.charAt(i);
    if ("]" == c) {
      if (outside) {
        return !1;
      }
      outside = !0;
    } else if ("[" == c) {
      if (!outside) {
        return !1;
      }
      outside = !1;
    } else if (!outside && !tokenRe.test(c)) {
      return !1;
    }
  }
  return outside;
}
var module$contents$goog$html$SafeStyle_VALUE_RE = RegExp("^[-,.\"'%_!#/ a-zA-Z0-9\\[\\]]+$"), module$contents$goog$html$SafeStyle_URL_RE = RegExp("\\b(url\\([ \t\n]*)('[ -&(-\\[\\]-~]*'|\"[ !#-\\[\\]-~]*\"|[!#-&*-\\[\\]-~]*)([ \t\n]*\\))", "g"), module$contents$goog$html$SafeStyle_ALLOWED_FUNCTIONS = "calc cubic-bezier fit-content hsl hsla linear-gradient matrix minmax radial-gradient repeat rgb rgba (rotate|scale|translate)(X|Y|Z|3d)? var".split(" "), module$contents$goog$html$SafeStyle_FUNCTIONS_RE = 
new RegExp("\\b(" + module$contents$goog$html$SafeStyle_ALLOWED_FUNCTIONS.join("|") + ")\\([-+*/0-9a-zA-Z.%#\\[\\], ]+\\)", "g"), module$contents$goog$html$SafeStyle_COMMENT_RE = /\/\*/;
function module$contents$goog$html$SafeStyle_sanitizeUrl(value) {
  return value.replace(module$contents$goog$html$SafeStyle_URL_RE, function(match$jscomp$0, before, url, after) {
    var quote = "";
    url = url.replace(/^(['"])(.*)\1$/, function(match, start, inside) {
      quote = start;
      return inside;
    });
    var sanitized = goog.html.SafeUrl.sanitize(url).getTypedStringValue();
    return before + quote + sanitized + quote + after;
  });
}
goog.html.SafeStyle = module$contents$goog$html$SafeStyle_SafeStyle;
var module$contents$goog$html$SafeStyleSheet_CONSTRUCTOR_TOKEN_PRIVATE = {}, module$contents$goog$html$SafeStyleSheet_SafeStyleSheet = function(value, token) {
  this.privateDoNotAccessOrElseSafeStyleSheetWrappedValue_ = token === module$contents$goog$html$SafeStyleSheet_CONSTRUCTOR_TOKEN_PRIVATE ? value : "";
  this.implementsGoogStringTypedString = !0;
};
module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.prototype.toString = function() {
  return this.privateDoNotAccessOrElseSafeStyleSheetWrappedValue_.toString();
};
module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.concat = function(var_args) {
  var result = "", addArgument = function(argument) {
    Array.isArray(argument) ? argument.forEach(addArgument) : result += module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.unwrap(argument);
  };
  Array.prototype.forEach.call(arguments, addArgument);
  return module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.createSafeStyleSheetSecurityPrivateDoNotAccessOrElse(result);
};
module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.fromConstant = function(styleSheet) {
  var styleSheetString = goog.string.Const.unwrap(styleSheet);
  if (0 === styleSheetString.length) {
    return module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.EMPTY;
  }
  (0,goog.asserts.assert)(!(0,goog.string.internal.contains)(styleSheetString, "<"), "Forbidden '<' character in style sheet string: " + styleSheetString);
  return module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.createSafeStyleSheetSecurityPrivateDoNotAccessOrElse(styleSheetString);
};
module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.prototype.getTypedStringValue = function() {
  return this.privateDoNotAccessOrElseSafeStyleSheetWrappedValue_;
};
module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.unwrap = function(safeStyleSheet) {
  if (safeStyleSheet instanceof module$contents$goog$html$SafeStyleSheet_SafeStyleSheet && safeStyleSheet.constructor === module$contents$goog$html$SafeStyleSheet_SafeStyleSheet) {
    return safeStyleSheet.privateDoNotAccessOrElseSafeStyleSheetWrappedValue_;
  }
  (0,goog.asserts.fail)("expected object of type SafeStyleSheet, got '" + safeStyleSheet + "' of type " + goog.typeOf(safeStyleSheet));
  return "type_error:SafeStyleSheet";
};
module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.createSafeStyleSheetSecurityPrivateDoNotAccessOrElse = function(styleSheet) {
  return new module$contents$goog$html$SafeStyleSheet_SafeStyleSheet(styleSheet, module$contents$goog$html$SafeStyleSheet_CONSTRUCTOR_TOKEN_PRIVATE);
};
module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.EMPTY = module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.createSafeStyleSheetSecurityPrivateDoNotAccessOrElse("");
goog.html.SafeStyleSheet = module$contents$goog$html$SafeStyleSheet_SafeStyleSheet;
var module$contents$goog$html$SafeHtml_CONSTRUCTOR_TOKEN_PRIVATE = {}, module$contents$goog$html$SafeHtml_SafeHtml = function(value, token) {
  this.privateDoNotAccessOrElseSafeHtmlWrappedValue_ = token === module$contents$goog$html$SafeHtml_CONSTRUCTOR_TOKEN_PRIVATE ? value : "";
  this.implementsGoogStringTypedString = !0;
};
module$contents$goog$html$SafeHtml_SafeHtml.prototype.getTypedStringValue = function() {
  return this.privateDoNotAccessOrElseSafeHtmlWrappedValue_.toString();
};
module$contents$goog$html$SafeHtml_SafeHtml.prototype.toString = function() {
  return this.privateDoNotAccessOrElseSafeHtmlWrappedValue_.toString();
};
module$contents$goog$html$SafeHtml_SafeHtml.unwrap = function(safeHtml) {
  return module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML(safeHtml).toString();
};
module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML = function(safeHtml) {
  if (safeHtml instanceof module$contents$goog$html$SafeHtml_SafeHtml && safeHtml.constructor === module$contents$goog$html$SafeHtml_SafeHtml) {
    return safeHtml.privateDoNotAccessOrElseSafeHtmlWrappedValue_;
  }
  goog.asserts.fail("expected object of type SafeHtml, got '" + safeHtml + "' of type " + goog.typeOf(safeHtml));
  return "type_error:SafeHtml";
};
module$contents$goog$html$SafeHtml_SafeHtml.htmlEscape = function(textOrHtml) {
  if (textOrHtml instanceof module$contents$goog$html$SafeHtml_SafeHtml) {
    return textOrHtml;
  }
  var textIsObject = "object" == typeof textOrHtml;
  var textAsString = textIsObject && textOrHtml.implementsGoogStringTypedString ? textOrHtml.getTypedStringValue() : String(textOrHtml);
  return module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlSecurityPrivateDoNotAccessOrElse(goog.string.internal.htmlEscape(textAsString));
};
module$contents$goog$html$SafeHtml_SafeHtml.create = function(tagName, attributes, content) {
  module$contents$goog$html$SafeHtml_SafeHtml.verifyTagName(String(tagName));
  return module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlTagSecurityPrivateDoNotAccessOrElse(String(tagName), attributes, content);
};
module$contents$goog$html$SafeHtml_SafeHtml.verifyTagName = function(tagName) {
  if (!module$contents$goog$html$SafeHtml_VALID_NAMES_IN_TAG.test(tagName)) {
    throw Error(module$contents$goog$html$SafeHtml_SafeHtml.ENABLE_ERROR_MESSAGES ? "Invalid tag name <" + tagName + ">." : "");
  }
  if (tagName.toUpperCase() in module$contents$goog$html$SafeHtml_NOT_ALLOWED_TAG_NAMES) {
    throw Error(module$contents$goog$html$SafeHtml_SafeHtml.ENABLE_ERROR_MESSAGES ? "Tag name <" + tagName + "> is not allowed for SafeHtml." : "");
  }
};
module$contents$goog$html$SafeHtml_SafeHtml.createScript = function(script, attributes) {
  for (var attr in attributes) {
    if (Object.prototype.hasOwnProperty.call(attributes, attr)) {
      var attrLower = attr.toLowerCase();
      if ("language" == attrLower || "src" == attrLower || "text" == attrLower) {
        throw Error(module$contents$goog$html$SafeHtml_SafeHtml.ENABLE_ERROR_MESSAGES ? 'Cannot set "' + attrLower + '" attribute' : "");
      }
    }
  }
  var content = "";
  script = module$contents$goog$array_concat(script);
  for (var i = 0; i < script.length; i++) {
    content += module$contents$goog$html$SafeScript_SafeScript.unwrap(script[i]);
  }
  var htmlContent = module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlSecurityPrivateDoNotAccessOrElse(content);
  return module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlTagSecurityPrivateDoNotAccessOrElse("script", attributes, htmlContent);
};
module$contents$goog$html$SafeHtml_SafeHtml.join = function(separator, parts) {
  var separatorHtml = module$contents$goog$html$SafeHtml_SafeHtml.htmlEscape(separator), content = [], addArgument = function(argument) {
    if (Array.isArray(argument)) {
      argument.forEach(addArgument);
    } else {
      var html = module$contents$goog$html$SafeHtml_SafeHtml.htmlEscape(argument);
      content.push(module$contents$goog$html$SafeHtml_SafeHtml.unwrap(html));
    }
  };
  parts.forEach(addArgument);
  return module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlSecurityPrivateDoNotAccessOrElse(content.join(module$contents$goog$html$SafeHtml_SafeHtml.unwrap(separatorHtml)));
};
module$contents$goog$html$SafeHtml_SafeHtml.concat = function(var_args) {
  return module$contents$goog$html$SafeHtml_SafeHtml.join(module$contents$goog$html$SafeHtml_SafeHtml.EMPTY, Array.prototype.slice.call(arguments));
};
module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlSecurityPrivateDoNotAccessOrElse = function(html) {
  var noinlineHtml = html, policy = goog.html.trustedtypes.getPolicyPrivateDoNotAccessOrElse(), trustedHtml = policy ? policy.createHTML(noinlineHtml) : noinlineHtml;
  return new module$contents$goog$html$SafeHtml_SafeHtml(trustedHtml, module$contents$goog$html$SafeHtml_CONSTRUCTOR_TOKEN_PRIVATE);
};
module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlTagSecurityPrivateDoNotAccessOrElse = function(tagName, attributes, content) {
  var result = "<" + tagName;
  result += module$contents$goog$html$SafeHtml_SafeHtml.stringifyAttributes(tagName, attributes);
  null == content ? content = [] : Array.isArray(content) || (content = [content]);
  if (goog.dom.tags.isVoidTag(tagName.toLowerCase())) {
    goog.asserts.assert(!content.length, "Void tag <" + tagName + "> does not allow content."), result += ">";
  } else {
    var html = module$contents$goog$html$SafeHtml_SafeHtml.concat(content);
    result += ">" + module$contents$goog$html$SafeHtml_SafeHtml.unwrap(html) + "</" + tagName + ">";
  }
  return module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlSecurityPrivateDoNotAccessOrElse(result);
};
module$contents$goog$html$SafeHtml_SafeHtml.stringifyAttributes = function(tagName$jscomp$0, attributes) {
  var result = "";
  if (attributes) {
    for (var name in attributes) {
      if (Object.prototype.hasOwnProperty.call(attributes, name)) {
        if (!module$contents$goog$html$SafeHtml_VALID_NAMES_IN_TAG.test(name)) {
          throw Error(module$contents$goog$html$SafeHtml_SafeHtml.ENABLE_ERROR_MESSAGES ? 'Invalid attribute name "' + name + '".' : "");
        }
        var value = attributes[name];
        if (null != value) {
          var JSCompiler_temp_const = result, tagName = tagName$jscomp$0, name$jscomp$0 = name, value$jscomp$0 = value;
          if (value$jscomp$0 instanceof goog.string.Const) {
            value$jscomp$0 = goog.string.Const.unwrap(value$jscomp$0);
          } else if ("style" == name$jscomp$0.toLowerCase()) {
            if (module$contents$goog$html$SafeHtml_SafeHtml.SUPPORT_STYLE_ATTRIBUTE) {
              var value$jscomp$1 = value$jscomp$0;
              if (!goog.isObject(value$jscomp$1)) {
                throw Error(module$contents$goog$html$SafeHtml_SafeHtml.ENABLE_ERROR_MESSAGES ? 'The "style" attribute requires goog.html.SafeStyle or map of style properties, ' + typeof value$jscomp$1 + " given: " + value$jscomp$1 : "");
              }
              value$jscomp$1 instanceof module$contents$goog$html$SafeStyle_SafeStyle || (value$jscomp$1 = module$contents$goog$html$SafeStyle_SafeStyle.create(value$jscomp$1));
              value$jscomp$0 = module$contents$goog$html$SafeStyle_SafeStyle.unwrap(value$jscomp$1);
            } else {
              throw Error(module$contents$goog$html$SafeHtml_SafeHtml.ENABLE_ERROR_MESSAGES ? 'Attribute "style" not supported.' : "");
            }
          } else {
            if (/^on/i.test(name$jscomp$0)) {
              throw Error(module$contents$goog$html$SafeHtml_SafeHtml.ENABLE_ERROR_MESSAGES ? 'Attribute "' + name$jscomp$0 + '" requires goog.string.Const value, "' + value$jscomp$0 + '" given.' : "");
            }
            if (name$jscomp$0.toLowerCase() in module$contents$goog$html$SafeHtml_URL_ATTRIBUTES) {
              if (value$jscomp$0 instanceof goog.html.TrustedResourceUrl) {
                value$jscomp$0 = goog.html.TrustedResourceUrl.unwrap(value$jscomp$0);
              } else if (value$jscomp$0 instanceof goog.html.SafeUrl) {
                value$jscomp$0 = goog.html.SafeUrl.unwrap(value$jscomp$0);
              } else if ("string" === typeof value$jscomp$0) {
                value$jscomp$0 = goog.html.SafeUrl.sanitize(value$jscomp$0).getTypedStringValue();
              } else {
                throw Error(module$contents$goog$html$SafeHtml_SafeHtml.ENABLE_ERROR_MESSAGES ? 'Attribute "' + name$jscomp$0 + '" on tag "' + tagName + '" requires goog.html.SafeUrl, goog.string.Const, or string, value "' + value$jscomp$0 + '" given.' : "");
              }
            }
          }
          value$jscomp$0.implementsGoogStringTypedString && (value$jscomp$0 = value$jscomp$0.getTypedStringValue());
          goog.asserts.assert("string" === typeof value$jscomp$0 || "number" === typeof value$jscomp$0, "String or number value expected, got " + typeof value$jscomp$0 + " with value: " + value$jscomp$0);
          var JSCompiler_inline_result = name$jscomp$0 + '="' + goog.string.internal.htmlEscape(String(value$jscomp$0)) + '"';
          result = JSCompiler_temp_const + (" " + JSCompiler_inline_result);
        }
      }
    }
  }
  return result;
};
module$contents$goog$html$SafeHtml_SafeHtml.ENABLE_ERROR_MESSAGES = goog.DEBUG;
module$contents$goog$html$SafeHtml_SafeHtml.SUPPORT_STYLE_ATTRIBUTE = !0;
module$contents$goog$html$SafeHtml_SafeHtml.from = module$contents$goog$html$SafeHtml_SafeHtml.htmlEscape;
var module$contents$goog$html$SafeHtml_VALID_NAMES_IN_TAG = /^[a-zA-Z0-9-]+$/, module$contents$goog$html$SafeHtml_URL_ATTRIBUTES = {action:!0, cite:!0, data:!0, formaction:!0, href:!0, manifest:!0, poster:!0, src:!0}, module$contents$goog$html$SafeHtml_NOT_ALLOWED_TAG_NAMES = module$contents$goog$object_createSet(goog.dom.TagName.APPLET, goog.dom.TagName.BASE, goog.dom.TagName.EMBED, goog.dom.TagName.IFRAME, goog.dom.TagName.LINK, goog.dom.TagName.MATH, goog.dom.TagName.META, goog.dom.TagName.OBJECT, 
goog.dom.TagName.SCRIPT, goog.dom.TagName.STYLE, goog.dom.TagName.SVG, goog.dom.TagName.TEMPLATE);
module$contents$goog$html$SafeHtml_SafeHtml.EMPTY = new module$contents$goog$html$SafeHtml_SafeHtml(goog.global.trustedTypes && goog.global.trustedTypes.emptyHTML || "", module$contents$goog$html$SafeHtml_CONSTRUCTOR_TOKEN_PRIVATE);
module$contents$goog$html$SafeHtml_SafeHtml.BR = module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlSecurityPrivateDoNotAccessOrElse("<br>");
goog.html.SafeHtml = module$contents$goog$html$SafeHtml_SafeHtml;
goog.html.uncheckedconversions = {};
goog.html.uncheckedconversions.safeHtmlFromStringKnownToSatisfyTypeContract = function(justification, html) {
  goog.asserts.assertString(goog.string.Const.unwrap(justification), "must provide justification");
  goog.asserts.assert(!goog.string.internal.isEmptyOrWhitespace(goog.string.Const.unwrap(justification)), "must provide non-empty justification");
  return module$contents$goog$html$SafeHtml_SafeHtml.createSafeHtmlSecurityPrivateDoNotAccessOrElse(html);
};
goog.html.uncheckedconversions.safeScriptFromStringKnownToSatisfyTypeContract = function(justification, script) {
  goog.asserts.assertString(goog.string.Const.unwrap(justification), "must provide justification");
  goog.asserts.assert(!goog.string.internal.isEmptyOrWhitespace(goog.string.Const.unwrap(justification)), "must provide non-empty justification");
  return module$contents$goog$html$SafeScript_SafeScript.createSafeScriptSecurityPrivateDoNotAccessOrElse(script);
};
goog.html.uncheckedconversions.safeStyleFromStringKnownToSatisfyTypeContract = function(justification, style) {
  goog.asserts.assertString(goog.string.Const.unwrap(justification), "must provide justification");
  goog.asserts.assert(!goog.string.internal.isEmptyOrWhitespace(goog.string.Const.unwrap(justification)), "must provide non-empty justification");
  return module$contents$goog$html$SafeStyle_SafeStyle.createSafeStyleSecurityPrivateDoNotAccessOrElse(style);
};
goog.html.uncheckedconversions.safeStyleSheetFromStringKnownToSatisfyTypeContract = function(justification, styleSheet) {
  goog.asserts.assertString(goog.string.Const.unwrap(justification), "must provide justification");
  goog.asserts.assert(!goog.string.internal.isEmptyOrWhitespace(goog.string.Const.unwrap(justification)), "must provide non-empty justification");
  return module$contents$goog$html$SafeStyleSheet_SafeStyleSheet.createSafeStyleSheetSecurityPrivateDoNotAccessOrElse(styleSheet);
};
goog.html.uncheckedconversions.safeUrlFromStringKnownToSatisfyTypeContract = function(justification, url) {
  goog.asserts.assertString(goog.string.Const.unwrap(justification), "must provide justification");
  goog.asserts.assert(!goog.string.internal.isEmptyOrWhitespace(goog.string.Const.unwrap(justification)), "must provide non-empty justification");
  return goog.html.SafeUrl.createSafeUrlSecurityPrivateDoNotAccessOrElse(url);
};
goog.html.uncheckedconversions.trustedResourceUrlFromStringKnownToSatisfyTypeContract = function(justification, url) {
  goog.asserts.assertString(goog.string.Const.unwrap(justification), "must provide justification");
  goog.asserts.assert(!goog.string.internal.isEmptyOrWhitespace(goog.string.Const.unwrap(justification)), "must provide non-empty justification");
  return goog.html.TrustedResourceUrl.createTrustedResourceUrlSecurityPrivateDoNotAccessOrElse(url);
};
goog.dom.safe = {};
goog.dom.safe.InsertAdjacentHtmlPosition = {AFTERBEGIN:"afterbegin", AFTEREND:"afterend", BEFOREBEGIN:"beforebegin", BEFOREEND:"beforeend"};
goog.dom.safe.insertAdjacentHtml = function(node, position, html) {
  node.insertAdjacentHTML(position, module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML(html));
};
goog.dom.safe.SET_INNER_HTML_DISALLOWED_TAGS_ = {MATH:!0, SCRIPT:!0, STYLE:!0, SVG:!0, TEMPLATE:!0};
goog.dom.safe.isInnerHtmlCleanupRecursive_ = goog.functions.cacheReturnValue(function() {
  if (goog.DEBUG && "undefined" === typeof document) {
    return !1;
  }
  var div = document.createElement("div"), childDiv = document.createElement("div");
  childDiv.appendChild(document.createElement("div"));
  div.appendChild(childDiv);
  if (goog.DEBUG && !div.firstChild) {
    return !1;
  }
  var innerChild = div.firstChild.firstChild;
  div.innerHTML = module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML(module$contents$goog$html$SafeHtml_SafeHtml.EMPTY);
  return !innerChild.parentElement;
});
goog.dom.safe.unsafeSetInnerHtmlDoNotUseOrElse = function(elem, html) {
  if (goog.dom.safe.isInnerHtmlCleanupRecursive_()) {
    for (; elem.lastChild;) {
      elem.removeChild(elem.lastChild);
    }
  }
  elem.innerHTML = module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML(html);
};
goog.dom.safe.setInnerHtml = function(elem, html) {
  if (goog.asserts.ENABLE_ASSERTS && elem.tagName) {
    var tagName = elem.tagName.toUpperCase();
    if (goog.dom.safe.SET_INNER_HTML_DISALLOWED_TAGS_[tagName]) {
      throw Error("goog.dom.safe.setInnerHtml cannot be used to set content of " + elem.tagName + ".");
    }
  }
  goog.dom.safe.unsafeSetInnerHtmlDoNotUseOrElse(elem, html);
};
goog.dom.safe.setInnerHtmlFromConstant = function(element, constHtml) {
  goog.dom.safe.setInnerHtml(element, goog.html.uncheckedconversions.safeHtmlFromStringKnownToSatisfyTypeContract(goog.string.Const.from("Constant HTML to be immediatelly used."), goog.string.Const.unwrap(constHtml)));
};
goog.dom.safe.setOuterHtml = function(elem, html) {
  elem.outerHTML = module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML(html);
};
goog.dom.safe.setFormElementAction = function(form, url) {
  var safeUrl = url instanceof goog.html.SafeUrl ? url : goog.html.SafeUrl.sanitizeAssertUnchanged(url);
  goog.dom.asserts.assertIsHTMLFormElement(form).action = goog.html.SafeUrl.unwrap(safeUrl);
};
goog.dom.safe.setButtonFormAction = function(button, url) {
  var safeUrl = url instanceof goog.html.SafeUrl ? url : goog.html.SafeUrl.sanitizeAssertUnchanged(url);
  goog.dom.asserts.assertIsHTMLButtonElement(button).formAction = goog.html.SafeUrl.unwrap(safeUrl);
};
goog.dom.safe.setInputFormAction = function(input, url) {
  var safeUrl = url instanceof goog.html.SafeUrl ? url : goog.html.SafeUrl.sanitizeAssertUnchanged(url);
  goog.dom.asserts.assertIsHTMLInputElement(input).formAction = goog.html.SafeUrl.unwrap(safeUrl);
};
goog.dom.safe.setStyle = function(elem, style) {
  elem.style.cssText = module$contents$goog$html$SafeStyle_SafeStyle.unwrap(style);
};
goog.dom.safe.documentWrite = function(doc, html) {
  doc.write(module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML(html));
};
goog.dom.safe.setAnchorHref = function(anchor, url) {
  goog.dom.asserts.assertIsHTMLAnchorElement(anchor);
  var safeUrl = url instanceof goog.html.SafeUrl ? url : goog.html.SafeUrl.sanitizeAssertUnchanged(url);
  anchor.href = goog.html.SafeUrl.unwrap(safeUrl);
};
goog.dom.safe.setImageSrc = function(imageElement, url) {
  goog.dom.asserts.assertIsHTMLImageElement(imageElement);
  if (url instanceof goog.html.SafeUrl) {
    var safeUrl = url;
  } else {
    var allowDataUrl = /^data:image\//i.test(url);
    safeUrl = goog.html.SafeUrl.sanitizeAssertUnchanged(url, allowDataUrl);
  }
  imageElement.src = goog.html.SafeUrl.unwrap(safeUrl);
};
goog.dom.safe.setAudioSrc = function(audioElement, url) {
  goog.dom.asserts.assertIsHTMLAudioElement(audioElement);
  if (url instanceof goog.html.SafeUrl) {
    var safeUrl = url;
  } else {
    var allowDataUrl = /^data:audio\//i.test(url);
    safeUrl = goog.html.SafeUrl.sanitizeAssertUnchanged(url, allowDataUrl);
  }
  audioElement.src = goog.html.SafeUrl.unwrap(safeUrl);
};
goog.dom.safe.setVideoSrc = function(videoElement, url) {
  goog.dom.asserts.assertIsHTMLVideoElement(videoElement);
  if (url instanceof goog.html.SafeUrl) {
    var safeUrl = url;
  } else {
    var allowDataUrl = /^data:video\//i.test(url);
    safeUrl = goog.html.SafeUrl.sanitizeAssertUnchanged(url, allowDataUrl);
  }
  videoElement.src = goog.html.SafeUrl.unwrap(safeUrl);
};
goog.dom.safe.setEmbedSrc = function(embed, url) {
  goog.dom.asserts.assertIsHTMLEmbedElement(embed);
  embed.src = goog.html.TrustedResourceUrl.unwrapTrustedScriptURL(url);
};
goog.dom.safe.setFrameSrc = function(frame, url) {
  goog.dom.asserts.assertIsHTMLFrameElement(frame);
  frame.src = goog.html.TrustedResourceUrl.unwrap(url);
};
goog.dom.safe.setIframeSrc = function(iframe, url) {
  goog.dom.asserts.assertIsHTMLIFrameElement(iframe);
  iframe.src = goog.html.TrustedResourceUrl.unwrap(url);
};
goog.dom.safe.setIframeSrcdoc = function(iframe, html) {
  goog.dom.asserts.assertIsHTMLIFrameElement(iframe);
  iframe.srcdoc = module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML(html);
};
goog.dom.safe.setLinkHrefAndRel = function(link, url, rel) {
  goog.dom.asserts.assertIsHTMLLinkElement(link);
  link.rel = rel;
  if (goog.string.internal.caseInsensitiveContains(rel, "stylesheet")) {
    goog.asserts.assert(url instanceof goog.html.TrustedResourceUrl, 'URL must be TrustedResourceUrl because "rel" contains "stylesheet"');
    link.href = goog.html.TrustedResourceUrl.unwrap(url);
    var win = link.ownerDocument && link.ownerDocument.defaultView, nonce = goog.dom.safe.getStyleNonce(win);
    nonce && link.setAttribute("nonce", nonce);
  } else {
    link.href = url instanceof goog.html.TrustedResourceUrl ? goog.html.TrustedResourceUrl.unwrap(url) : url instanceof goog.html.SafeUrl ? goog.html.SafeUrl.unwrap(url) : goog.html.SafeUrl.unwrap(goog.html.SafeUrl.sanitizeAssertUnchanged(url));
  }
};
goog.dom.safe.setObjectData = function(object, url) {
  goog.dom.asserts.assertIsHTMLObjectElement(object);
  object.data = goog.html.TrustedResourceUrl.unwrapTrustedScriptURL(url);
};
goog.dom.safe.setScriptSrc = function(script, url) {
  goog.dom.asserts.assertIsHTMLScriptElement(script);
  goog.dom.safe.setNonceForScriptElement_(script);
  script.src = goog.html.TrustedResourceUrl.unwrapTrustedScriptURL(url);
};
goog.dom.safe.setScriptContent = function(script, content) {
  goog.dom.asserts.assertIsHTMLScriptElement(script);
  goog.dom.safe.setNonceForScriptElement_(script);
  script.textContent = module$contents$goog$html$SafeScript_SafeScript.unwrapTrustedScript(content);
};
goog.dom.safe.setNonceForScriptElement_ = function(script) {
  var win = script.ownerDocument && script.ownerDocument.defaultView, nonce = goog.dom.safe.getScriptNonce(win);
  nonce && script.setAttribute("nonce", nonce);
};
goog.dom.safe.setLocationHref = function(loc, url) {
  goog.dom.asserts.assertIsLocation(loc);
  var safeUrl = url instanceof goog.html.SafeUrl ? url : goog.html.SafeUrl.sanitizeAssertUnchanged(url);
  loc.href = goog.html.SafeUrl.unwrap(safeUrl);
};
goog.dom.safe.assignLocation = function(loc, url) {
  goog.dom.asserts.assertIsLocation(loc);
  var safeUrl = url instanceof goog.html.SafeUrl ? url : goog.html.SafeUrl.sanitizeAssertUnchanged(url);
  loc.assign(goog.html.SafeUrl.unwrap(safeUrl));
};
goog.dom.safe.replaceLocation = function(loc, url) {
  var safeUrl = url instanceof goog.html.SafeUrl ? url : goog.html.SafeUrl.sanitizeAssertUnchanged(url);
  loc.replace(goog.html.SafeUrl.unwrap(safeUrl));
};
goog.dom.safe.openInWindow = function(url, opt_openerWin, opt_name, opt_specs) {
  var safeUrl = url instanceof goog.html.SafeUrl ? url : goog.html.SafeUrl.sanitizeAssertUnchanged(url);
  var win = opt_openerWin || goog.global, name = opt_name instanceof goog.string.Const ? goog.string.Const.unwrap(opt_name) : opt_name || "";
  return void 0 !== opt_specs ? win.open(goog.html.SafeUrl.unwrap(safeUrl), name, opt_specs) : win.open(goog.html.SafeUrl.unwrap(safeUrl), name);
};
goog.dom.safe.parseFromStringHtml = function(parser, html) {
  return goog.dom.safe.parseFromString(parser, html, "text/html");
};
goog.dom.safe.parseFromString = function(parser, content, type) {
  return parser.parseFromString(module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML(content), type);
};
goog.dom.safe.createImageFromBlob = function(blob) {
  if (!/^image\/.*/g.test(blob.type)) {
    throw Error("goog.dom.safe.createImageFromBlob only accepts MIME type image/.*.");
  }
  var objectUrl = goog.global.URL.createObjectURL(blob), image = new goog.global.Image();
  image.onload = function() {
    goog.global.URL.revokeObjectURL(objectUrl);
  };
  goog.dom.safe.setImageSrc(image, goog.html.uncheckedconversions.safeUrlFromStringKnownToSatisfyTypeContract(goog.string.Const.from("Image blob URL."), objectUrl));
  return image;
};
goog.dom.safe.createContextualFragment = function(range, html) {
  return range.createContextualFragment(module$contents$goog$html$SafeHtml_SafeHtml.unwrapTrustedHTML(html));
};
goog.dom.safe.getScriptNonce = function(opt_window) {
  return goog.dom.safe.getNonce_("script[nonce]", opt_window);
};
goog.dom.safe.getStyleNonce = function(opt_window) {
  return goog.dom.safe.getNonce_('style[nonce],link[rel="stylesheet"][nonce]', opt_window);
};
goog.dom.safe.NONCE_PATTERN_ = /^[\w+/_-]+[=]{0,2}$/;
goog.dom.safe.getNonce_ = function(selector, win) {
  var doc = (win || goog.global).document;
  if (!doc.querySelector) {
    return "";
  }
  var el = doc.querySelector(selector);
  if (el) {
    var nonce = el.nonce || el.getAttribute("nonce");
    if (nonce && goog.dom.safe.NONCE_PATTERN_.test(nonce)) {
      return nonce;
    }
  }
  return "";
};
goog.math = {};
goog.math.randomInt = function(a) {
  return Math.floor(Math.random() * a);
};
goog.math.uniformRandom = function(a, b) {
  return a + Math.random() * (b - a);
};
goog.math.clamp = function(value, min, max) {
  return Math.min(Math.max(value, min), max);
};
goog.math.modulo = function(a, b) {
  var r = a % b;
  return 0 > r * b ? r + b : r;
};
goog.math.lerp = function(a, b, x) {
  return a + x * (b - a);
};
goog.math.nearlyEquals = function(a, b, opt_tolerance) {
  return Math.abs(a - b) <= (opt_tolerance || 1E-6);
};
goog.math.standardAngle = function(angle) {
  return goog.math.modulo(angle, 360);
};
goog.math.standardAngleInRadians = function(angle) {
  return goog.math.modulo(angle, 2 * Math.PI);
};
goog.math.toRadians = function(angleDegrees) {
  return angleDegrees * Math.PI / 180;
};
goog.math.toDegrees = function(angleRadians) {
  return 180 * angleRadians / Math.PI;
};
goog.math.angleDx = function(degrees, radius) {
  return radius * Math.cos(goog.math.toRadians(degrees));
};
goog.math.angleDy = function(degrees, radius) {
  return radius * Math.sin(goog.math.toRadians(degrees));
};
goog.math.angle = function(x1, y1, x2, y2) {
  return goog.math.standardAngle(goog.math.toDegrees(Math.atan2(y2 - y1, x2 - x1)));
};
goog.math.angleDifference = function(startAngle, endAngle) {
  var d = goog.math.standardAngle(endAngle) - goog.math.standardAngle(startAngle);
  180 < d ? d -= 360 : -180 >= d && (d = 360 + d);
  return d;
};
goog.math.sign = function(x) {
  return 0 < x ? 1 : 0 > x ? -1 : x;
};
goog.math.longestCommonSubsequence = function(array1, array2, opt_compareFn, opt_collectorFn) {
  for (var compare = opt_compareFn || function(a, b) {
    return a == b;
  }, collect = opt_collectorFn || function(i1) {
    return array1[i1];
  }, length1 = array1.length, length2 = array2.length, arr = [], i = 0; i < length1 + 1; i++) {
    arr[i] = [], arr[i][0] = 0;
  }
  for (var j = 0; j < length2 + 1; j++) {
    arr[0][j] = 0;
  }
  for (i = 1; i <= length1; i++) {
    for (j = 1; j <= length2; j++) {
      compare(array1[i - 1], array2[j - 1]) ? arr[i][j] = arr[i - 1][j - 1] + 1 : arr[i][j] = Math.max(arr[i - 1][j], arr[i][j - 1]);
    }
  }
  var result = [];
  i = length1;
  for (j = length2; 0 < i && 0 < j;) {
    compare(array1[i - 1], array2[j - 1]) ? (result.unshift(collect(i - 1, j - 1)), i--, j--) : arr[i - 1][j] > arr[i][j - 1] ? i-- : j--;
  }
  return result;
};
goog.math.sum = function(var_args) {
  return Array.prototype.reduce.call(arguments, function(sum, value) {
    return sum + value;
  }, 0);
};
goog.math.average = function(var_args) {
  return goog.math.sum.apply(null, arguments) / arguments.length;
};
goog.math.sampleVariance = function(var_args) {
  var sampleSize = arguments.length;
  if (2 > sampleSize) {
    return 0;
  }
  var mean = goog.math.average.apply(null, arguments), variance = goog.math.sum.apply(null, Array.prototype.map.call(arguments, function(val) {
    return Math.pow(val - mean, 2);
  })) / (sampleSize - 1);
  return variance;
};
goog.math.standardDeviation = function(var_args) {
  return Math.sqrt(goog.math.sampleVariance.apply(null, arguments));
};
goog.math.isInt = function(num) {
  return isFinite(num) && 0 == num % 1;
};
goog.math.isFiniteNumber = function(num) {
  return isFinite(num);
};
goog.math.isNegativeZero = function(num) {
  return 0 == num && 0 > 1 / num;
};
goog.math.log10Floor = function(num) {
  if (0 < num) {
    var x = Math.round(Math.log(num) * Math.LOG10E);
    return x - (parseFloat("1e" + x) > num ? 1 : 0);
  }
  return 0 == num ? -Infinity : NaN;
};
goog.math.safeFloor = function(num, opt_epsilon) {
  goog.asserts.assert(void 0 === opt_epsilon || 0 < opt_epsilon);
  return Math.floor(num + (opt_epsilon || 2E-15));
};
goog.math.safeCeil = function(num, opt_epsilon) {
  goog.asserts.assert(void 0 === opt_epsilon || 0 < opt_epsilon);
  return Math.ceil(num - (opt_epsilon || 2E-15));
};
goog.math.Coordinate = function(opt_x, opt_y) {
  this.x = void 0 !== opt_x ? opt_x : 0;
  this.y = void 0 !== opt_y ? opt_y : 0;
};
goog.math.Coordinate.prototype.clone = function() {
  return new goog.math.Coordinate(this.x, this.y);
};
goog.DEBUG && (goog.math.Coordinate.prototype.toString = function() {
  return "(" + this.x + ", " + this.y + ")";
});
goog.math.Coordinate.prototype.equals = function(other) {
  return other instanceof goog.math.Coordinate && goog.math.Coordinate.equals(this, other);
};
goog.math.Coordinate.equals = function(a, b) {
  return a == b ? !0 : a && b ? a.x == b.x && a.y == b.y : !1;
};
goog.math.Coordinate.distance = function(a, b) {
  var dx = a.x - b.x, dy = a.y - b.y;
  return Math.sqrt(dx * dx + dy * dy);
};
goog.math.Coordinate.magnitude = function(a) {
  return Math.sqrt(a.x * a.x + a.y * a.y);
};
goog.math.Coordinate.azimuth = function(a) {
  return goog.math.angle(0, 0, a.x, a.y);
};
goog.math.Coordinate.squaredDistance = function(a, b) {
  var dx = a.x - b.x, dy = a.y - b.y;
  return dx * dx + dy * dy;
};
goog.math.Coordinate.difference = function(a, b) {
  return new goog.math.Coordinate(a.x - b.x, a.y - b.y);
};
goog.math.Coordinate.sum = function(a, b) {
  return new goog.math.Coordinate(a.x + b.x, a.y + b.y);
};
goog.math.Coordinate.prototype.ceil = function() {
  this.x = Math.ceil(this.x);
  this.y = Math.ceil(this.y);
  return this;
};
goog.math.Coordinate.prototype.floor = function() {
  this.x = Math.floor(this.x);
  this.y = Math.floor(this.y);
  return this;
};
goog.math.Coordinate.prototype.round = function() {
  this.x = Math.round(this.x);
  this.y = Math.round(this.y);
  return this;
};
goog.math.Coordinate.prototype.translate = function(tx, opt_ty) {
  tx instanceof goog.math.Coordinate ? (this.x += tx.x, this.y += tx.y) : (this.x += Number(tx), "number" === typeof opt_ty && (this.y += opt_ty));
  return this;
};
goog.math.Coordinate.prototype.scale = function(sx, opt_sy) {
  var sy = "number" === typeof opt_sy ? opt_sy : sx;
  this.x *= sx;
  this.y *= sy;
  return this;
};
goog.math.Size = function(width, height) {
  this.width = width;
  this.height = height;
};
goog.math.Size.equals = function(a, b) {
  return a == b ? !0 : a && b ? a.width == b.width && a.height == b.height : !1;
};
goog.math.Size.prototype.clone = function() {
  return new goog.math.Size(this.width, this.height);
};
goog.DEBUG && (goog.math.Size.prototype.toString = function() {
  return "(" + this.width + " x " + this.height + ")";
});
goog.math.Size.prototype.area = function() {
  return this.width * this.height;
};
goog.math.Size.prototype.aspectRatio = function() {
  return this.width / this.height;
};
goog.math.Size.prototype.isEmpty = function() {
  return !this.area();
};
goog.math.Size.prototype.ceil = function() {
  this.width = Math.ceil(this.width);
  this.height = Math.ceil(this.height);
  return this;
};
goog.math.Size.prototype.floor = function() {
  this.width = Math.floor(this.width);
  this.height = Math.floor(this.height);
  return this;
};
goog.math.Size.prototype.round = function() {
  this.width = Math.round(this.width);
  this.height = Math.round(this.height);
  return this;
};
goog.math.Size.prototype.scale = function(sx, opt_sy) {
  var sy = "number" === typeof opt_sy ? opt_sy : sx;
  this.width *= sx;
  this.height *= sy;
  return this;
};
goog.string.DETECT_DOUBLE_ESCAPING = !1;
goog.string.FORCE_NON_DOM_HTML_UNESCAPING = !1;
goog.string.Unicode = {NBSP:"\u00a0"};
goog.string.startsWith = goog.string.internal.startsWith;
goog.string.endsWith = goog.string.internal.endsWith;
goog.string.caseInsensitiveStartsWith = goog.string.internal.caseInsensitiveStartsWith;
goog.string.caseInsensitiveEndsWith = goog.string.internal.caseInsensitiveEndsWith;
goog.string.caseInsensitiveEquals = goog.string.internal.caseInsensitiveEquals;
goog.string.subs = function(str, var_args) {
  for (var splitParts = str.split("%s"), returnString = "", subsArguments = Array.prototype.slice.call(arguments, 1); subsArguments.length && 1 < splitParts.length;) {
    returnString += splitParts.shift() + subsArguments.shift();
  }
  return returnString + splitParts.join("%s");
};
goog.string.collapseWhitespace = function(str) {
  return str.replace(/[\s\xa0]+/g, " ").replace(/^\s+|\s+$/g, "");
};
goog.string.isEmptyOrWhitespace = goog.string.internal.isEmptyOrWhitespace;
goog.string.isEmptyString = function(str) {
  return 0 == str.length;
};
goog.string.isEmpty = goog.string.isEmptyOrWhitespace;
goog.string.isEmptyOrWhitespaceSafe = function(str) {
  return goog.string.isEmptyOrWhitespace(goog.string.makeSafe(str));
};
goog.string.isEmptySafe = goog.string.isEmptyOrWhitespaceSafe;
goog.string.isBreakingWhitespace = function(str) {
  return !/[^\t\n\r ]/.test(str);
};
goog.string.isAlpha = function(str) {
  return !/[^a-zA-Z]/.test(str);
};
goog.string.isNumeric = function(str) {
  return !/[^0-9]/.test(str);
};
goog.string.isAlphaNumeric = function(str) {
  return !/[^a-zA-Z0-9]/.test(str);
};
goog.string.isSpace = function(ch) {
  return " " == ch;
};
goog.string.isUnicodeChar = function(ch) {
  return 1 == ch.length && " " <= ch && "~" >= ch || "\u0080" <= ch && "\ufffd" >= ch;
};
goog.string.stripNewlines = function(str) {
  return str.replace(/(\r\n|\r|\n)+/g, " ");
};
goog.string.canonicalizeNewlines = function(str) {
  return str.replace(/(\r\n|\r|\n)/g, "\n");
};
goog.string.normalizeWhitespace = function(str) {
  return str.replace(/\xa0|\s/g, " ");
};
goog.string.normalizeSpaces = function(str) {
  return str.replace(/\xa0|[ \t]+/g, " ");
};
goog.string.collapseBreakingSpaces = function(str) {
  return str.replace(/[\t\r\n ]+/g, " ").replace(/^[\t\r\n ]+|[\t\r\n ]+$/g, "");
};
goog.string.trim = goog.string.internal.trim;
goog.string.trimLeft = function(str) {
  return str.replace(/^[\s\xa0]+/, "");
};
goog.string.trimRight = function(str) {
  return str.replace(/[\s\xa0]+$/, "");
};
goog.string.caseInsensitiveCompare = goog.string.internal.caseInsensitiveCompare;
goog.string.numberAwareCompare_ = function(str1, str2, tokenizerRegExp) {
  if (str1 == str2) {
    return 0;
  }
  if (!str1) {
    return -1;
  }
  if (!str2) {
    return 1;
  }
  for (var tokens1 = str1.toLowerCase().match(tokenizerRegExp), tokens2 = str2.toLowerCase().match(tokenizerRegExp), count = Math.min(tokens1.length, tokens2.length), i = 0; i < count; i++) {
    var a = tokens1[i], b = tokens2[i];
    if (a != b) {
      var num1 = parseInt(a, 10);
      if (!isNaN(num1)) {
        var num2 = parseInt(b, 10);
        if (!isNaN(num2) && num1 - num2) {
          return num1 - num2;
        }
      }
      return a < b ? -1 : 1;
    }
  }
  return tokens1.length != tokens2.length ? tokens1.length - tokens2.length : str1 < str2 ? -1 : 1;
};
goog.string.intAwareCompare = function(str1, str2) {
  return goog.string.numberAwareCompare_(str1, str2, /\d+|\D+/g);
};
goog.string.floatAwareCompare = function(str1, str2) {
  return goog.string.numberAwareCompare_(str1, str2, /\d+|\.\d+|\D+/g);
};
goog.string.numerateCompare = goog.string.floatAwareCompare;
goog.string.urlEncode = function(str) {
  return encodeURIComponent(String(str));
};
goog.string.urlDecode = function(str) {
  return decodeURIComponent(str.replace(/\+/g, " "));
};
goog.string.newLineToBr = goog.string.internal.newLineToBr;
goog.string.htmlEscape = function(str, opt_isLikelyToContainHtmlChars) {
  str = goog.string.internal.htmlEscape(str, opt_isLikelyToContainHtmlChars);
  goog.string.DETECT_DOUBLE_ESCAPING && (str = str.replace(goog.string.E_RE_, "&#101;"));
  return str;
};
goog.string.E_RE_ = /e/g;
goog.string.unescapeEntities = function(str) {
  return goog.string.contains(str, "&") ? !goog.string.FORCE_NON_DOM_HTML_UNESCAPING && "document" in goog.global ? goog.string.unescapeEntitiesUsingDom_(str) : goog.string.unescapePureXmlEntities_(str) : str;
};
goog.string.unescapeEntitiesWithDocument = function(str, document) {
  return goog.string.contains(str, "&") ? goog.string.unescapeEntitiesUsingDom_(str, document) : str;
};
goog.string.unescapeEntitiesUsingDom_ = function(str, opt_document) {
  var seen = {"&amp;":"&", "&lt;":"<", "&gt;":">", "&quot;":'"'};
  var div = opt_document ? opt_document.createElement("div") : goog.global.document.createElement("div");
  return str.replace(goog.string.HTML_ENTITY_PATTERN_, function(s, entity) {
    var value = seen[s];
    if (value) {
      return value;
    }
    if ("#" == entity.charAt(0)) {
      var n = Number("0" + entity.slice(1));
      isNaN(n) || (value = String.fromCharCode(n));
    }
    value || (goog.dom.safe.setInnerHtml(div, goog.html.uncheckedconversions.safeHtmlFromStringKnownToSatisfyTypeContract(goog.string.Const.from("Single HTML entity."), s + " ")), value = div.firstChild.nodeValue.slice(0, -1));
    return seen[s] = value;
  });
};
goog.string.unescapePureXmlEntities_ = function(str) {
  return str.replace(/&([^;]+);/g, function(s, entity) {
    switch(entity) {
      case "amp":
        return "&";
      case "lt":
        return "<";
      case "gt":
        return ">";
      case "quot":
        return '"';
      default:
        if ("#" == entity.charAt(0)) {
          var n = Number("0" + entity.slice(1));
          if (!isNaN(n)) {
            return String.fromCharCode(n);
          }
        }
        return s;
    }
  });
};
goog.string.HTML_ENTITY_PATTERN_ = /&([^;\s<&]+);?/g;
goog.string.whitespaceEscape = function(str, opt_xml) {
  return goog.string.newLineToBr(str.replace(/  /g, " &#160;"), opt_xml);
};
goog.string.preserveSpaces = function(str) {
  return str.replace(/(^|[\n ]) /g, "$1" + goog.string.Unicode.NBSP);
};
goog.string.stripQuotes = function(str, quoteChars) {
  for (var length = quoteChars.length, i = 0; i < length; i++) {
    var quoteChar = 1 == length ? quoteChars : quoteChars.charAt(i);
    if (str.charAt(0) == quoteChar && str.charAt(str.length - 1) == quoteChar) {
      return str.substring(1, str.length - 1);
    }
  }
  return str;
};
goog.string.truncate = function(str, chars, opt_protectEscapedCharacters) {
  opt_protectEscapedCharacters && (str = goog.string.unescapeEntities(str));
  str.length > chars && (str = str.substring(0, chars - 3) + "...");
  opt_protectEscapedCharacters && (str = goog.string.htmlEscape(str));
  return str;
};
goog.string.truncateMiddle = function(str, chars, opt_protectEscapedCharacters, opt_trailingChars) {
  opt_protectEscapedCharacters && (str = goog.string.unescapeEntities(str));
  if (opt_trailingChars && str.length > chars) {
    opt_trailingChars > chars && (opt_trailingChars = chars);
    var endPoint = str.length - opt_trailingChars, startPoint = chars - opt_trailingChars;
    str = str.substring(0, startPoint) + "..." + str.substring(endPoint);
  } else if (str.length > chars) {
    var half = Math.floor(chars / 2), endPos = str.length - half;
    half += chars % 2;
    str = str.substring(0, half) + "..." + str.substring(endPos);
  }
  opt_protectEscapedCharacters && (str = goog.string.htmlEscape(str));
  return str;
};
goog.string.specialEscapeChars_ = {"\x00":"\\0", "\b":"\\b", "\f":"\\f", "\n":"\\n", "\r":"\\r", "\t":"\\t", "\v":"\\x0B", '"':'\\"', "\\":"\\\\", "<":"\\u003C"};
goog.string.jsEscapeCache_ = {"'":"\\'"};
goog.string.quote = function(s) {
  s = String(s);
  for (var sb = ['"'], i = 0; i < s.length; i++) {
    var ch = s.charAt(i), cc = ch.charCodeAt(0);
    sb[i + 1] = goog.string.specialEscapeChars_[ch] || (31 < cc && 127 > cc ? ch : goog.string.escapeChar(ch));
  }
  sb.push('"');
  return sb.join("");
};
goog.string.escapeString = function(str) {
  for (var sb = [], i = 0; i < str.length; i++) {
    sb[i] = goog.string.escapeChar(str.charAt(i));
  }
  return sb.join("");
};
goog.string.escapeChar = function(c) {
  if (c in goog.string.jsEscapeCache_) {
    return goog.string.jsEscapeCache_[c];
  }
  if (c in goog.string.specialEscapeChars_) {
    return goog.string.jsEscapeCache_[c] = goog.string.specialEscapeChars_[c];
  }
  var cc = c.charCodeAt(0);
  if (31 < cc && 127 > cc) {
    var rv = c;
  } else {
    if (256 > cc) {
      if (rv = "\\x", 16 > cc || 256 < cc) {
        rv += "0";
      }
    } else {
      rv = "\\u", 4096 > cc && (rv += "0");
    }
    rv += cc.toString(16).toUpperCase();
  }
  return goog.string.jsEscapeCache_[c] = rv;
};
goog.string.contains = goog.string.internal.contains;
goog.string.caseInsensitiveContains = goog.string.internal.caseInsensitiveContains;
goog.string.countOf = function(s, ss) {
  return s && ss ? s.split(ss).length - 1 : 0;
};
goog.string.removeAt = function(s, index, stringLength) {
  var resultStr = s;
  0 <= index && index < s.length && 0 < stringLength && (resultStr = s.slice(0, index) + s.slice(index + stringLength));
  return resultStr;
};
goog.string.remove = function(str, substr) {
  return str.replace(substr, "");
};
goog.string.removeAll = function(s, ss) {
  var re = new RegExp(goog.string.regExpEscape(ss), "g");
  return s.replace(re, "");
};
goog.string.replaceAll = function(s, ss, replacement) {
  var re = new RegExp(goog.string.regExpEscape(ss), "g");
  return s.replace(re, replacement.replace(/\$/g, "$$$$"));
};
goog.string.regExpEscape = function(s) {
  return String(s).replace(/([-()\[\]{}+?*.$\^|,:#<!\\])/g, "\\$1").replace(/\x08/g, "\\x08");
};
goog.string.repeat = String.prototype.repeat ? function(string, length) {
  return string.repeat(length);
} : function(string, length) {
  return Array(length + 1).join(string);
};
goog.string.padNumber = function(num, length, opt_precision) {
  if (!Number.isFinite(num)) {
    return String(num);
  }
  var s = void 0 !== opt_precision ? num.toFixed(opt_precision) : String(num), index = s.indexOf(".");
  -1 === index && (index = s.length);
  var sign = "-" === s[0] ? "-" : "";
  sign && (s = s.substring(1));
  return sign + goog.string.repeat("0", Math.max(0, length - index)) + s;
};
goog.string.makeSafe = function(obj) {
  return null == obj ? "" : String(obj);
};
goog.string.getRandomString = function() {
  return Math.floor(2147483648 * Math.random()).toString(36) + Math.abs(Math.floor(2147483648 * Math.random()) ^ goog.now()).toString(36);
};
goog.string.compareVersions = goog.string.internal.compareVersions;
goog.string.hashCode = function(str) {
  for (var result = 0, i = 0; i < str.length; ++i) {
    result = 31 * result + str.charCodeAt(i) >>> 0;
  }
  return result;
};
goog.string.uniqueStringCounter_ = 2147483648 * Math.random() | 0;
goog.string.createUniqueString = function() {
  return "goog_" + goog.string.uniqueStringCounter_++;
};
goog.string.toNumber = function(str) {
  var num = Number(str);
  return 0 == num && goog.string.isEmptyOrWhitespace(str) ? NaN : num;
};
goog.string.isLowerCamelCase = function(str) {
  return /^[a-z]+([A-Z][a-z]*)*$/.test(str);
};
goog.string.isUpperCamelCase = function(str) {
  return /^([A-Z][a-z]*)+$/.test(str);
};
goog.string.toCamelCase = function(str) {
  return String(str).replace(/\-([a-z])/g, function(all, match) {
    return match.toUpperCase();
  });
};
goog.string.toSelectorCase = function(str) {
  return String(str).replace(/([A-Z])/g, "-$1").toLowerCase();
};
goog.string.toTitleCase = function(str, opt_delimiters) {
  var delimiters = "string" === typeof opt_delimiters ? goog.string.regExpEscape(opt_delimiters) : "\\s";
  delimiters = delimiters ? "|[" + delimiters + "]+" : "";
  var regexp = new RegExp("(^" + delimiters + ")([a-z])", "g");
  return str.replace(regexp, function(all, p1, p2) {
    return p1 + p2.toUpperCase();
  });
};
goog.string.capitalize = function(str) {
  return String(str.charAt(0)).toUpperCase() + String(str.slice(1)).toLowerCase();
};
goog.string.parseInt = function(value) {
  isFinite(value) && (value = String(value));
  return "string" === typeof value ? /^\s*-?0x/i.test(value) ? parseInt(value, 16) : parseInt(value, 10) : NaN;
};
goog.string.splitLimit = function(str, separator, limit) {
  for (var parts = str.split(separator), returnVal = []; 0 < limit && parts.length;) {
    returnVal.push(parts.shift()), limit--;
  }
  parts.length && returnVal.push(parts.join(separator));
  return returnVal;
};
goog.string.lastComponent = function(str, separators) {
  if (separators) {
    "string" == typeof separators && (separators = [separators]);
  } else {
    return str;
  }
  for (var lastSeparatorIndex = -1, i = 0; i < separators.length; i++) {
    if ("" != separators[i]) {
      var currentSeparatorIndex = str.lastIndexOf(separators[i]);
      currentSeparatorIndex > lastSeparatorIndex && (lastSeparatorIndex = currentSeparatorIndex);
    }
  }
  return -1 == lastSeparatorIndex ? str : str.slice(lastSeparatorIndex + 1);
};
goog.string.editDistance = function(a, b) {
  var v0 = [], v1 = [];
  if (a == b) {
    return 0;
  }
  if (!a.length || !b.length) {
    return Math.max(a.length, b.length);
  }
  for (var i = 0; i < b.length + 1; i++) {
    v0[i] = i;
  }
  for (var i$18 = 0; i$18 < a.length; i$18++) {
    v1[0] = i$18 + 1;
    for (var j = 0; j < b.length; j++) {
      var cost = Number(a[i$18] != b[j]);
      v1[j + 1] = Math.min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost);
    }
    for (var j$19 = 0; j$19 < v0.length; j$19++) {
      v0[j$19] = v1[j$19];
    }
  }
  return v1[b.length];
};
goog.dom.Appendable = {};
goog.dom.ASSUME_QUIRKS_MODE = !1;
goog.dom.ASSUME_STANDARDS_MODE = !1;
goog.dom.COMPAT_MODE_KNOWN_ = goog.dom.ASSUME_QUIRKS_MODE || goog.dom.ASSUME_STANDARDS_MODE;
goog.dom.getDomHelper = function(opt_element) {
  return opt_element ? new goog.dom.DomHelper(goog.dom.getOwnerDocument(opt_element)) : goog.dom.defaultDomHelper_ || (goog.dom.defaultDomHelper_ = new goog.dom.DomHelper());
};
goog.dom.getDocument = function() {
  return document;
};
goog.dom.getElement = function(element) {
  return goog.dom.getElementHelper_(document, element);
};
goog.dom.getHTMLElement = function(id) {
  var element = goog.dom.getElement(id);
  return element ? goog.asserts.assertInstanceof(element, HTMLElement) : null;
};
goog.dom.getElementHelper_ = function(doc, element) {
  return "string" === typeof element ? doc.getElementById(element) : element;
};
goog.dom.getRequiredElement = function(id) {
  return goog.dom.getRequiredElementHelper_(document, id);
};
goog.dom.getRequiredHTMLElement = function(id) {
  return goog.asserts.assertInstanceof(goog.dom.getRequiredElementHelper_(document, id), HTMLElement);
};
goog.dom.getRequiredElementHelper_ = function(doc, id) {
  goog.asserts.assertString(id);
  var element = goog.dom.getElementHelper_(doc, id);
  return element = goog.asserts.assertElement(element, "No element found with id: " + id);
};
goog.dom.$ = goog.dom.getElement;
goog.dom.getElementsByTagName = function(tagName, opt_parent) {
  var parent = opt_parent || document;
  return parent.getElementsByTagName(String(tagName));
};
goog.dom.getElementsByTagNameAndClass = function(opt_tag, opt_class, opt_el) {
  return goog.dom.getElementsByTagNameAndClass_(document, opt_tag, opt_class, opt_el);
};
goog.dom.getElementByTagNameAndClass = function(opt_tag, opt_class, opt_el) {
  return goog.dom.getElementByTagNameAndClass_(document, opt_tag, opt_class, opt_el);
};
goog.dom.getElementsByClass = function(className, opt_el) {
  var parent = opt_el || document;
  return goog.dom.canUseQuerySelector_(parent) ? parent.querySelectorAll("." + className) : goog.dom.getElementsByTagNameAndClass_(document, "*", className, opt_el);
};
goog.dom.getElementByClass = function(className, opt_el) {
  var parent = opt_el || document, retVal;
  return (retVal = parent.getElementsByClassName ? parent.getElementsByClassName(className)[0] : goog.dom.getElementByTagNameAndClass_(document, "*", className, opt_el)) || null;
};
goog.dom.getHTMLElementByClass = function(className, opt_parent) {
  var element = goog.dom.getElementByClass(className, opt_parent);
  return element ? goog.asserts.assertInstanceof(element, HTMLElement) : null;
};
goog.dom.getRequiredElementByClass = function(className, opt_root) {
  var retValue = goog.dom.getElementByClass(className, opt_root);
  return goog.asserts.assert(retValue, "No element found with className: " + className);
};
goog.dom.getRequiredHTMLElementByClass = function(className, opt_parent) {
  var retValue = goog.dom.getElementByClass(className, opt_parent);
  return goog.asserts.assertInstanceof(retValue, HTMLElement, "No HTMLElement found with className: " + className);
};
goog.dom.canUseQuerySelector_ = function(parent) {
  return !(!parent.querySelectorAll || !parent.querySelector);
};
goog.dom.getElementsByTagNameAndClass_ = function(doc, opt_tag, opt_class, opt_el) {
  var parent = opt_el || doc, tagName = opt_tag && "*" != opt_tag ? String(opt_tag).toUpperCase() : "";
  if (goog.dom.canUseQuerySelector_(parent) && (tagName || opt_class)) {
    var query = tagName + (opt_class ? "." + opt_class : "");
    return parent.querySelectorAll(query);
  }
  if (opt_class && parent.getElementsByClassName) {
    var els = parent.getElementsByClassName(opt_class);
    if (tagName) {
      for (var arrayLike = {}, len = 0, i = 0, el; el = els[i]; i++) {
        tagName == el.nodeName && (arrayLike[len++] = el);
      }
      arrayLike.length = len;
      return arrayLike;
    }
    return els;
  }
  els = parent.getElementsByTagName(tagName || "*");
  if (opt_class) {
    arrayLike = {};
    for (i = len = 0; el = els[i]; i++) {
      var className = el.className;
      "function" == typeof className.split && module$contents$goog$array_contains(className.split(/\s+/), opt_class) && (arrayLike[len++] = el);
    }
    arrayLike.length = len;
    return arrayLike;
  }
  return els;
};
goog.dom.getElementByTagNameAndClass_ = function(doc, opt_tag, opt_class, opt_el) {
  var parent = opt_el || doc, tag = opt_tag && "*" != opt_tag ? String(opt_tag).toUpperCase() : "";
  if (goog.dom.canUseQuerySelector_(parent) && (tag || opt_class)) {
    return parent.querySelector(tag + (opt_class ? "." + opt_class : ""));
  }
  var elements = goog.dom.getElementsByTagNameAndClass_(doc, opt_tag, opt_class, opt_el);
  return elements[0] || null;
};
goog.dom.$$ = goog.dom.getElementsByTagNameAndClass;
goog.dom.setProperties = function(element, properties) {
  module$contents$goog$object_forEach(properties, function(val, key) {
    val && "object" == typeof val && val.implementsGoogStringTypedString && (val = val.getTypedStringValue());
    "style" == key ? element.style.cssText = val : "class" == key ? element.className = val : "for" == key ? element.htmlFor = val : goog.dom.DIRECT_ATTRIBUTE_MAP_.hasOwnProperty(key) ? element.setAttribute(goog.dom.DIRECT_ATTRIBUTE_MAP_[key], val) : goog.string.startsWith(key, "aria-") || goog.string.startsWith(key, "data-") ? element.setAttribute(key, val) : element[key] = val;
  });
};
goog.dom.DIRECT_ATTRIBUTE_MAP_ = {cellpadding:"cellPadding", cellspacing:"cellSpacing", colspan:"colSpan", frameborder:"frameBorder", height:"height", maxlength:"maxLength", nonce:"nonce", role:"role", rowspan:"rowSpan", type:"type", usemap:"useMap", valign:"vAlign", width:"width"};
goog.dom.getViewportSize = function(opt_window) {
  return goog.dom.getViewportSize_(opt_window || window);
};
goog.dom.getViewportSize_ = function(win) {
  var doc = win.document, el = goog.dom.isCss1CompatMode_(doc) ? doc.documentElement : doc.body;
  return new goog.math.Size(el.clientWidth, el.clientHeight);
};
goog.dom.getDocumentHeight = function() {
  return goog.dom.getDocumentHeight_(window);
};
goog.dom.getDocumentHeightForWindow = function(win) {
  return goog.dom.getDocumentHeight_(win);
};
goog.dom.getDocumentHeight_ = function(win) {
  var doc = win.document, height = 0;
  if (doc) {
    var body = doc.body, docEl = doc.documentElement;
    if (!docEl || !body) {
      return 0;
    }
    var vh = goog.dom.getViewportSize_(win).height;
    if (goog.dom.isCss1CompatMode_(doc) && docEl.scrollHeight) {
      height = docEl.scrollHeight != vh ? docEl.scrollHeight : docEl.offsetHeight;
    } else {
      var sh = docEl.scrollHeight, oh = docEl.offsetHeight;
      docEl.clientHeight != oh && (sh = body.scrollHeight, oh = body.offsetHeight);
      height = sh > vh ? sh > oh ? sh : oh : sh < oh ? sh : oh;
    }
  }
  return height;
};
goog.dom.getPageScroll = function(opt_window) {
  var win = opt_window || goog.global || window;
  return goog.dom.getDomHelper(win.document).getDocumentScroll();
};
goog.dom.getDocumentScroll = function() {
  return goog.dom.getDocumentScroll_(document);
};
goog.dom.getDocumentScroll_ = function(doc) {
  var el = goog.dom.getDocumentScrollElement_(doc), win = goog.dom.getWindow_(doc);
  return goog.userAgent.IE && goog.userAgent.isVersionOrHigher("10") && win.pageYOffset != el.scrollTop ? new goog.math.Coordinate(el.scrollLeft, el.scrollTop) : new goog.math.Coordinate(win.pageXOffset || el.scrollLeft, win.pageYOffset || el.scrollTop);
};
goog.dom.getDocumentScrollElement = function() {
  return goog.dom.getDocumentScrollElement_(document);
};
goog.dom.getDocumentScrollElement_ = function(doc) {
  return doc.scrollingElement ? doc.scrollingElement : !goog.userAgent.WEBKIT && goog.dom.isCss1CompatMode_(doc) ? doc.documentElement : doc.body || doc.documentElement;
};
goog.dom.getWindow = function(opt_doc) {
  return opt_doc ? goog.dom.getWindow_(opt_doc) : window;
};
goog.dom.getWindow_ = function(doc) {
  return doc.parentWindow || doc.defaultView;
};
goog.dom.createDom = function(tagName, opt_attributes, var_args) {
  return goog.dom.createDom_(document, arguments);
};
goog.dom.createDom_ = function(doc, args) {
  var tagName = String(args[0]), attributes = args[1], element = goog.dom.createElement_(doc, tagName);
  attributes && ("string" === typeof attributes ? element.className = attributes : Array.isArray(attributes) ? element.className = attributes.join(" ") : goog.dom.setProperties(element, attributes));
  2 < args.length && goog.dom.append_(doc, element, args, 2);
  return element;
};
goog.dom.append_ = function(doc, parent, args, startIndex) {
  function childHandler(child) {
    child && parent.appendChild("string" === typeof child ? doc.createTextNode(child) : child);
  }
  for (var i = startIndex; i < args.length; i++) {
    var arg = args[i];
    goog.isArrayLike(arg) && !goog.dom.isNodeLike(arg) ? module$contents$goog$array_forEach(goog.dom.isNodeList(arg) ? module$contents$goog$array_toArray(arg) : arg, childHandler) : childHandler(arg);
  }
};
goog.dom.$dom = goog.dom.createDom;
goog.dom.createElement = function(name) {
  return goog.dom.createElement_(document, name);
};
goog.dom.createElement_ = function(doc, name) {
  name = String(name);
  "application/xhtml+xml" === doc.contentType && (name = name.toLowerCase());
  return doc.createElement(name);
};
goog.dom.createTextNode = function(content) {
  return document.createTextNode(String(content));
};
goog.dom.createTable = function(rows, columns, opt_fillWithNbsp) {
  return goog.dom.createTable_(document, rows, columns, !!opt_fillWithNbsp);
};
goog.dom.createTable_ = function(doc, rows, columns, fillWithNbsp) {
  for (var table = goog.dom.createElement_(doc, goog.dom.TagName.TABLE), tbody = table.appendChild(goog.dom.createElement_(doc, goog.dom.TagName.TBODY)), i = 0; i < rows; i++) {
    for (var tr = goog.dom.createElement_(doc, goog.dom.TagName.TR), j = 0; j < columns; j++) {
      var td = goog.dom.createElement_(doc, goog.dom.TagName.TD);
      fillWithNbsp && goog.dom.setTextContent(td, goog.string.Unicode.NBSP);
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  }
  return table;
};
goog.dom.constHtmlToNode = function(var_args) {
  var stringArray = Array.prototype.map.call(arguments, goog.string.Const.unwrap), safeHtml = goog.html.uncheckedconversions.safeHtmlFromStringKnownToSatisfyTypeContract(goog.string.Const.from("Constant HTML string, that gets turned into a Node later, so it will be automatically balanced."), stringArray.join(""));
  return goog.dom.safeHtmlToNode(safeHtml);
};
goog.dom.safeHtmlToNode = function(html) {
  return goog.dom.safeHtmlToNode_(document, html);
};
goog.dom.safeHtmlToNode_ = function(doc, html) {
  var tempDiv = goog.dom.createElement_(doc, goog.dom.TagName.DIV);
  goog.userAgent.IE ? (goog.dom.safe.setInnerHtml(tempDiv, module$contents$goog$html$SafeHtml_SafeHtml.concat(module$contents$goog$html$SafeHtml_SafeHtml.BR, html)), tempDiv.removeChild(goog.asserts.assert(tempDiv.firstChild))) : goog.dom.safe.setInnerHtml(tempDiv, html);
  return goog.dom.childrenToNode_(doc, tempDiv);
};
goog.dom.childrenToNode_ = function(doc, tempDiv) {
  if (1 == tempDiv.childNodes.length) {
    return tempDiv.removeChild(goog.asserts.assert(tempDiv.firstChild));
  }
  for (var fragment = doc.createDocumentFragment(); tempDiv.firstChild;) {
    fragment.appendChild(tempDiv.firstChild);
  }
  return fragment;
};
goog.dom.isCss1CompatMode = function() {
  return goog.dom.isCss1CompatMode_(document);
};
goog.dom.isCss1CompatMode_ = function(doc) {
  return goog.dom.COMPAT_MODE_KNOWN_ ? goog.dom.ASSUME_STANDARDS_MODE : "CSS1Compat" == doc.compatMode;
};
goog.dom.canHaveChildren = function(node) {
  if (node.nodeType != goog.dom.NodeType.ELEMENT) {
    return !1;
  }
  switch(node.tagName) {
    case String(goog.dom.TagName.APPLET):
    case String(goog.dom.TagName.AREA):
    case String(goog.dom.TagName.BASE):
    case String(goog.dom.TagName.BR):
    case String(goog.dom.TagName.COL):
    case String(goog.dom.TagName.COMMAND):
    case String(goog.dom.TagName.EMBED):
    case String(goog.dom.TagName.FRAME):
    case String(goog.dom.TagName.HR):
    case String(goog.dom.TagName.IMG):
    case String(goog.dom.TagName.INPUT):
    case String(goog.dom.TagName.IFRAME):
    case String(goog.dom.TagName.ISINDEX):
    case String(goog.dom.TagName.KEYGEN):
    case String(goog.dom.TagName.LINK):
    case String(goog.dom.TagName.NOFRAMES):
    case String(goog.dom.TagName.NOSCRIPT):
    case String(goog.dom.TagName.META):
    case String(goog.dom.TagName.OBJECT):
    case String(goog.dom.TagName.PARAM):
    case String(goog.dom.TagName.SCRIPT):
    case String(goog.dom.TagName.SOURCE):
    case String(goog.dom.TagName.STYLE):
    case String(goog.dom.TagName.TRACK):
    case String(goog.dom.TagName.WBR):
      return !1;
  }
  return !0;
};
goog.dom.appendChild = function(parent, child) {
  goog.asserts.assert(null != parent && null != child, "goog.dom.appendChild expects non-null arguments");
  parent.appendChild(child);
};
goog.dom.append = function(parent, var_args) {
  goog.dom.append_(goog.dom.getOwnerDocument(parent), parent, arguments, 1);
};
goog.dom.removeChildren = function(node) {
  for (var child; child = node.firstChild;) {
    node.removeChild(child);
  }
};
goog.dom.insertSiblingBefore = function(newNode, refNode) {
  goog.asserts.assert(null != newNode && null != refNode, "goog.dom.insertSiblingBefore expects non-null arguments");
  refNode.parentNode && refNode.parentNode.insertBefore(newNode, refNode);
};
goog.dom.insertSiblingAfter = function(newNode, refNode) {
  goog.asserts.assert(null != newNode && null != refNode, "goog.dom.insertSiblingAfter expects non-null arguments");
  refNode.parentNode && refNode.parentNode.insertBefore(newNode, refNode.nextSibling);
};
goog.dom.insertChildAt = function(parent, child, index) {
  goog.asserts.assert(null != parent, "goog.dom.insertChildAt expects a non-null parent");
  parent.insertBefore(child, parent.childNodes[index] || null);
};
goog.dom.removeNode = function(node) {
  return node && node.parentNode ? node.parentNode.removeChild(node) : null;
};
goog.dom.replaceNode = function(newNode, oldNode) {
  goog.asserts.assert(null != newNode && null != oldNode, "goog.dom.replaceNode expects non-null arguments");
  var parent = oldNode.parentNode;
  parent && parent.replaceChild(newNode, oldNode);
};
goog.dom.copyContents = function(target, source) {
  goog.asserts.assert(null != target && null != source, "goog.dom.copyContents expects non-null arguments");
  var childNodes = source.cloneNode(!0).childNodes;
  for (goog.dom.removeChildren(target); childNodes.length;) {
    target.appendChild(childNodes[0]);
  }
};
goog.dom.flattenElement = function(element) {
  var child, parent = element.parentNode;
  if (parent && parent.nodeType != goog.dom.NodeType.DOCUMENT_FRAGMENT) {
    if (element.removeNode) {
      return element.removeNode(!1);
    }
    for (; child = element.firstChild;) {
      parent.insertBefore(child, element);
    }
    return goog.dom.removeNode(element);
  }
};
goog.dom.getChildren = function(element) {
  return void 0 != element.children ? element.children : Array.prototype.filter.call(element.childNodes, function(node) {
    return node.nodeType == goog.dom.NodeType.ELEMENT;
  });
};
goog.dom.getFirstElementChild = function(node) {
  return void 0 !== node.firstElementChild ? node.firstElementChild : goog.dom.getNextElementNode_(node.firstChild, !0);
};
goog.dom.getLastElementChild = function(node) {
  return void 0 !== node.lastElementChild ? node.lastElementChild : goog.dom.getNextElementNode_(node.lastChild, !1);
};
goog.dom.getNextElementSibling = function(node) {
  return void 0 !== node.nextElementSibling ? node.nextElementSibling : goog.dom.getNextElementNode_(node.nextSibling, !0);
};
goog.dom.getPreviousElementSibling = function(node) {
  return void 0 !== node.previousElementSibling ? node.previousElementSibling : goog.dom.getNextElementNode_(node.previousSibling, !1);
};
goog.dom.getNextElementNode_ = function(node, forward) {
  for (; node && node.nodeType != goog.dom.NodeType.ELEMENT;) {
    node = forward ? node.nextSibling : node.previousSibling;
  }
  return node;
};
goog.dom.getNextNode = function(node) {
  if (!node) {
    return null;
  }
  if (node.firstChild) {
    return node.firstChild;
  }
  for (; node && !node.nextSibling;) {
    node = node.parentNode;
  }
  return node ? node.nextSibling : null;
};
goog.dom.getPreviousNode = function(node) {
  if (!node) {
    return null;
  }
  if (!node.previousSibling) {
    return node.parentNode;
  }
  for (node = node.previousSibling; node && node.lastChild;) {
    node = node.lastChild;
  }
  return node;
};
goog.dom.isNodeLike = function(obj) {
  return goog.isObject(obj) && 0 < obj.nodeType;
};
goog.dom.isElement = function(obj) {
  return goog.isObject(obj) && obj.nodeType == goog.dom.NodeType.ELEMENT;
};
goog.dom.isWindow = function(obj) {
  return goog.isObject(obj) && obj.window == obj;
};
goog.dom.getParentElement = function(element) {
  var parent;
  if (goog.dom.BrowserFeature.CAN_USE_PARENT_ELEMENT_PROPERTY) {
    var isIe9 = goog.userAgent.IE && goog.userAgent.isVersionOrHigher("9") && !goog.userAgent.isVersionOrHigher("10");
    if (!(isIe9 && goog.global.SVGElement && element instanceof goog.global.SVGElement) && (parent = element.parentElement)) {
      return parent;
    }
  }
  parent = element.parentNode;
  return goog.dom.isElement(parent) ? parent : null;
};
goog.dom.contains = function(parent, descendant) {
  if (!parent || !descendant) {
    return !1;
  }
  if (parent.contains && descendant.nodeType == goog.dom.NodeType.ELEMENT) {
    return parent == descendant || parent.contains(descendant);
  }
  if ("undefined" != typeof parent.compareDocumentPosition) {
    return parent == descendant || !!(parent.compareDocumentPosition(descendant) & 16);
  }
  for (; descendant && parent != descendant;) {
    descendant = descendant.parentNode;
  }
  return descendant == parent;
};
goog.dom.compareNodeOrder = function(node1, node2) {
  if (node1 == node2) {
    return 0;
  }
  if (node1.compareDocumentPosition) {
    return node1.compareDocumentPosition(node2) & 2 ? 1 : -1;
  }
  if (goog.userAgent.IE && !goog.userAgent.isDocumentModeOrHigher(9)) {
    if (node1.nodeType == goog.dom.NodeType.DOCUMENT) {
      return -1;
    }
    if (node2.nodeType == goog.dom.NodeType.DOCUMENT) {
      return 1;
    }
  }
  if ("sourceIndex" in node1 || node1.parentNode && "sourceIndex" in node1.parentNode) {
    var isElement1 = node1.nodeType == goog.dom.NodeType.ELEMENT, isElement2 = node2.nodeType == goog.dom.NodeType.ELEMENT;
    if (isElement1 && isElement2) {
      return node1.sourceIndex - node2.sourceIndex;
    }
    var parent1 = node1.parentNode, parent2 = node2.parentNode;
    return parent1 == parent2 ? goog.dom.compareSiblingOrder_(node1, node2) : !isElement1 && goog.dom.contains(parent1, node2) ? -1 * goog.dom.compareParentsDescendantNodeIe_(node1, node2) : !isElement2 && goog.dom.contains(parent2, node1) ? goog.dom.compareParentsDescendantNodeIe_(node2, node1) : (isElement1 ? node1.sourceIndex : parent1.sourceIndex) - (isElement2 ? node2.sourceIndex : parent2.sourceIndex);
  }
  var doc = goog.dom.getOwnerDocument(node1);
  var range1 = doc.createRange();
  range1.selectNode(node1);
  range1.collapse(!0);
  var range2 = doc.createRange();
  range2.selectNode(node2);
  range2.collapse(!0);
  return range1.compareBoundaryPoints(goog.global.Range.START_TO_END, range2);
};
goog.dom.compareParentsDescendantNodeIe_ = function(textNode, node) {
  var parent = textNode.parentNode;
  if (parent == node) {
    return -1;
  }
  for (var sibling = node; sibling.parentNode != parent;) {
    sibling = sibling.parentNode;
  }
  return goog.dom.compareSiblingOrder_(sibling, textNode);
};
goog.dom.compareSiblingOrder_ = function(node1, node2) {
  for (var s = node2; s = s.previousSibling;) {
    if (s == node1) {
      return -1;
    }
  }
  return 1;
};
goog.dom.findCommonAncestor = function(var_args) {
  var i, count = arguments.length;
  if (!count) {
    return null;
  }
  if (1 == count) {
    return arguments[0];
  }
  var paths = [], minLength = Infinity;
  for (i = 0; i < count; i++) {
    for (var ancestors = [], node = arguments[i]; node;) {
      ancestors.unshift(node), node = node.parentNode;
    }
    paths.push(ancestors);
    minLength = Math.min(minLength, ancestors.length);
  }
  var output = null;
  for (i = 0; i < minLength; i++) {
    for (var first = paths[0][i], j = 1; j < count; j++) {
      if (first != paths[j][i]) {
        return output;
      }
    }
    output = first;
  }
  return output;
};
goog.dom.isInDocument = function(node) {
  return 16 == (node.ownerDocument.compareDocumentPosition(node) & 16);
};
goog.dom.getOwnerDocument = function(node) {
  goog.asserts.assert(node, "Node cannot be null or undefined.");
  return node.nodeType == goog.dom.NodeType.DOCUMENT ? node : node.ownerDocument || node.document;
};
goog.dom.getFrameContentDocument = function(frame) {
  return frame.contentDocument || frame.contentWindow.document;
};
goog.dom.getFrameContentWindow = function(frame) {
  try {
    return frame.contentWindow || (frame.contentDocument ? goog.dom.getWindow(frame.contentDocument) : null);
  } catch (e) {
  }
  return null;
};
goog.dom.setTextContent = function(node, text) {
  goog.asserts.assert(null != node, "goog.dom.setTextContent expects a non-null value for node");
  if ("textContent" in node) {
    node.textContent = text;
  } else if (node.nodeType == goog.dom.NodeType.TEXT) {
    node.data = String(text);
  } else if (node.firstChild && node.firstChild.nodeType == goog.dom.NodeType.TEXT) {
    for (; node.lastChild != node.firstChild;) {
      node.removeChild(goog.asserts.assert(node.lastChild));
    }
    node.firstChild.data = String(text);
  } else {
    goog.dom.removeChildren(node);
    var doc = goog.dom.getOwnerDocument(node);
    node.appendChild(doc.createTextNode(String(text)));
  }
};
goog.dom.getOuterHtml = function(element) {
  goog.asserts.assert(null !== element, "goog.dom.getOuterHtml expects a non-null value for element");
  if ("outerHTML" in element) {
    return element.outerHTML;
  }
  var doc = goog.dom.getOwnerDocument(element), div = goog.dom.createElement_(doc, goog.dom.TagName.DIV);
  div.appendChild(element.cloneNode(!0));
  return div.innerHTML;
};
goog.dom.findNode = function(root, p) {
  var rv = [], found = goog.dom.findNodes_(root, p, rv, !0);
  return found ? rv[0] : void 0;
};
goog.dom.findNodes = function(root, p) {
  var rv = [];
  goog.dom.findNodes_(root, p, rv, !1);
  return rv;
};
goog.dom.findNodes_ = function(root, p, rv, findOne) {
  if (null != root) {
    for (var child = root.firstChild; child;) {
      if (p(child) && (rv.push(child), findOne) || goog.dom.findNodes_(child, p, rv, findOne)) {
        return !0;
      }
      child = child.nextSibling;
    }
  }
  return !1;
};
goog.dom.findElement = function(root, pred) {
  for (var stack = goog.dom.getChildrenReverse_(root); 0 < stack.length;) {
    var next = stack.pop();
    if (pred(next)) {
      return next;
    }
    for (var c = next.lastElementChild; c; c = c.previousElementSibling) {
      stack.push(c);
    }
  }
  return null;
};
goog.dom.findElements = function(root, pred) {
  for (var result = [], stack = goog.dom.getChildrenReverse_(root); 0 < stack.length;) {
    var next = stack.pop();
    pred(next) && result.push(next);
    for (var c = next.lastElementChild; c; c = c.previousElementSibling) {
      stack.push(c);
    }
  }
  return result;
};
goog.dom.getChildrenReverse_ = function(node) {
  if (node.nodeType == goog.dom.NodeType.DOCUMENT) {
    return [node.documentElement];
  }
  for (var children = [], c = node.lastElementChild; c; c = c.previousElementSibling) {
    children.push(c);
  }
  return children;
};
goog.dom.TAGS_TO_IGNORE_ = {SCRIPT:1, STYLE:1, HEAD:1, IFRAME:1, OBJECT:1};
goog.dom.PREDEFINED_TAG_VALUES_ = {IMG:" ", BR:"\n"};
goog.dom.isFocusableTabIndex = function(element) {
  return goog.dom.hasSpecifiedTabIndex_(element) && goog.dom.isTabIndexFocusable_(element);
};
goog.dom.setFocusableTabIndex = function(element, enable) {
  enable ? element.tabIndex = 0 : (element.tabIndex = -1, element.removeAttribute("tabIndex"));
};
goog.dom.isFocusable = function(element) {
  var focusable;
  return (focusable = goog.dom.nativelySupportsFocus_(element) ? !element.disabled && (!goog.dom.hasSpecifiedTabIndex_(element) || goog.dom.isTabIndexFocusable_(element)) : goog.dom.isFocusableTabIndex(element)) && goog.userAgent.IE ? goog.dom.hasNonZeroBoundingRect_(element) : focusable;
};
goog.dom.hasSpecifiedTabIndex_ = function(element) {
  return element.hasAttribute("tabindex");
};
goog.dom.isTabIndexFocusable_ = function(element) {
  var index = element.tabIndex;
  return "number" === typeof index && 0 <= index && 32768 > index;
};
goog.dom.nativelySupportsFocus_ = function(element) {
  return element.tagName == goog.dom.TagName.A && element.hasAttribute("href") || element.tagName == goog.dom.TagName.INPUT || element.tagName == goog.dom.TagName.TEXTAREA || element.tagName == goog.dom.TagName.SELECT || element.tagName == goog.dom.TagName.BUTTON;
};
goog.dom.hasNonZeroBoundingRect_ = function(element) {
  var rect = "function" !== typeof element.getBoundingClientRect || goog.userAgent.IE && null == element.parentElement ? {height:element.offsetHeight, width:element.offsetWidth} : element.getBoundingClientRect();
  return null != rect && 0 < rect.height && 0 < rect.width;
};
goog.dom.getTextContent = function(node) {
  var buf = [];
  goog.dom.getTextContent_(node, buf, !0);
  var textContent = buf.join("");
  textContent = textContent.replace(/ \xAD /g, " ").replace(/\xAD/g, "");
  textContent = textContent.replace(/\u200B/g, "");
  textContent = textContent.replace(/ +/g, " ");
  " " != textContent && (textContent = textContent.replace(/^\s*/, ""));
  return textContent;
};
goog.dom.getRawTextContent = function(node) {
  var buf = [];
  goog.dom.getTextContent_(node, buf, !1);
  return buf.join("");
};
goog.dom.getTextContent_ = function(node, buf, normalizeWhitespace) {
  if (!(node.nodeName in goog.dom.TAGS_TO_IGNORE_)) {
    if (node.nodeType == goog.dom.NodeType.TEXT) {
      normalizeWhitespace ? buf.push(String(node.nodeValue).replace(/(\r\n|\r|\n)/g, "")) : buf.push(node.nodeValue);
    } else if (node.nodeName in goog.dom.PREDEFINED_TAG_VALUES_) {
      buf.push(goog.dom.PREDEFINED_TAG_VALUES_[node.nodeName]);
    } else {
      for (var child = node.firstChild; child;) {
        goog.dom.getTextContent_(child, buf, normalizeWhitespace), child = child.nextSibling;
      }
    }
  }
};
goog.dom.getNodeTextLength = function(node) {
  return goog.dom.getTextContent(node).length;
};
goog.dom.getNodeTextOffset = function(node, opt_offsetParent) {
  for (var root = opt_offsetParent || goog.dom.getOwnerDocument(node).body, buf = []; node && node != root;) {
    for (var cur = node; cur = cur.previousSibling;) {
      buf.unshift(goog.dom.getTextContent(cur));
    }
    node = node.parentNode;
  }
  return goog.string.trimLeft(buf.join("")).replace(/ +/g, " ").length;
};
goog.dom.getNodeAtOffset = function(parent, offset, opt_result) {
  for (var stack = [parent], pos = 0, cur = null; 0 < stack.length && pos < offset;) {
    if (cur = stack.pop(), !(cur.nodeName in goog.dom.TAGS_TO_IGNORE_)) {
      if (cur.nodeType == goog.dom.NodeType.TEXT) {
        var text = cur.nodeValue.replace(/(\r\n|\r|\n)/g, "").replace(/ +/g, " ");
        pos += text.length;
      } else if (cur.nodeName in goog.dom.PREDEFINED_TAG_VALUES_) {
        pos += goog.dom.PREDEFINED_TAG_VALUES_[cur.nodeName].length;
      } else {
        for (var i = cur.childNodes.length - 1; 0 <= i; i--) {
          stack.push(cur.childNodes[i]);
        }
      }
    }
  }
  goog.isObject(opt_result) && (opt_result.remainder = cur ? cur.nodeValue.length + offset - pos - 1 : 0, opt_result.node = cur);
  return cur;
};
goog.dom.isNodeList = function(val) {
  if (val && "number" == typeof val.length) {
    if (goog.isObject(val)) {
      return "function" == typeof val.item || "string" == typeof val.item;
    }
    if ("function" === typeof val) {
      return "function" == typeof val.item;
    }
  }
  return !1;
};
goog.dom.getAncestorByTagNameAndClass = function(element, opt_tag, opt_class, opt_maxSearchSteps) {
  if (!opt_tag && !opt_class) {
    return null;
  }
  var tagName = opt_tag ? String(opt_tag).toUpperCase() : null;
  return goog.dom.getAncestor(element, function(node) {
    return (!tagName || node.nodeName == tagName) && (!opt_class || "string" === typeof node.className && module$contents$goog$array_contains(node.className.split(/\s+/), opt_class));
  }, !0, opt_maxSearchSteps);
};
goog.dom.getAncestorByClass = function(element, className, opt_maxSearchSteps) {
  return goog.dom.getAncestorByTagNameAndClass(element, null, className, opt_maxSearchSteps);
};
goog.dom.getAncestor = function(element, matcher, opt_includeNode, opt_maxSearchSteps) {
  element && !opt_includeNode && (element = element.parentNode);
  for (var steps = 0; element && (null == opt_maxSearchSteps || steps <= opt_maxSearchSteps);) {
    goog.asserts.assert("parentNode" != element.name);
    if (matcher(element)) {
      return element;
    }
    element = element.parentNode;
    steps++;
  }
  return null;
};
goog.dom.getActiveElement = function(doc) {
  try {
    var activeElement = doc && doc.activeElement;
    return activeElement && activeElement.nodeName ? activeElement : null;
  } catch (e) {
    return null;
  }
};
goog.dom.getPixelRatio = function() {
  var win = goog.dom.getWindow();
  return void 0 !== win.devicePixelRatio ? win.devicePixelRatio : win.matchMedia ? goog.dom.matchesPixelRatio_(3) || goog.dom.matchesPixelRatio_(2) || goog.dom.matchesPixelRatio_(1.5) || goog.dom.matchesPixelRatio_(1) || .75 : 1;
};
goog.dom.matchesPixelRatio_ = function(pixelRatio) {
  var win = goog.dom.getWindow(), query = "(min-resolution: " + pixelRatio + "dppx),(min--moz-device-pixel-ratio: " + pixelRatio + "),(min-resolution: " + 96 * pixelRatio + "dpi)";
  return win.matchMedia(query).matches ? pixelRatio : 0;
};
goog.dom.getCanvasContext2D = function(canvas) {
  return canvas.getContext("2d");
};
goog.dom.DomHelper = function(opt_document) {
  this.document_ = opt_document || goog.global.document || document;
};
goog.dom.DomHelper.prototype.getDomHelper = goog.dom.getDomHelper;
goog.dom.DomHelper.prototype.getDocument = function() {
  return this.document_;
};
goog.dom.DomHelper.prototype.getElement = function(element) {
  return goog.dom.getElementHelper_(this.document_, element);
};
goog.dom.DomHelper.prototype.getRequiredElement = function(id) {
  return goog.dom.getRequiredElementHelper_(this.document_, id);
};
goog.dom.DomHelper.prototype.$ = goog.dom.DomHelper.prototype.getElement;
goog.dom.DomHelper.prototype.getElementsByTagName = function(tagName, opt_parent) {
  var parent = opt_parent || this.document_;
  return parent.getElementsByTagName(String(tagName));
};
goog.dom.DomHelper.prototype.getElementsByTagNameAndClass = function(opt_tag, opt_class, opt_el) {
  return goog.dom.getElementsByTagNameAndClass_(this.document_, opt_tag, opt_class, opt_el);
};
goog.dom.DomHelper.prototype.getElementByTagNameAndClass = function(opt_tag, opt_class, opt_el) {
  return goog.dom.getElementByTagNameAndClass_(this.document_, opt_tag, opt_class, opt_el);
};
goog.dom.DomHelper.prototype.getElementsByClass = function(className, opt_el) {
  var doc = opt_el || this.document_;
  return goog.dom.getElementsByClass(className, doc);
};
goog.dom.DomHelper.prototype.getElementByClass = function(className, opt_el) {
  var doc = opt_el || this.document_;
  return goog.dom.getElementByClass(className, doc);
};
goog.dom.DomHelper.prototype.getRequiredElementByClass = function(className, opt_root) {
  var root = opt_root || this.document_;
  return goog.dom.getRequiredElementByClass(className, root);
};
goog.dom.DomHelper.prototype.$$ = goog.dom.DomHelper.prototype.getElementsByTagNameAndClass;
goog.dom.DomHelper.prototype.setProperties = goog.dom.setProperties;
goog.dom.DomHelper.prototype.getViewportSize = function(opt_window) {
  return goog.dom.getViewportSize(opt_window || this.getWindow());
};
goog.dom.DomHelper.prototype.getDocumentHeight = function() {
  return goog.dom.getDocumentHeight_(this.getWindow());
};
goog.dom.DomHelper.prototype.createDom = function(tagName, opt_attributes, var_args) {
  return goog.dom.createDom_(this.document_, arguments);
};
goog.dom.DomHelper.prototype.$dom = goog.dom.DomHelper.prototype.createDom;
goog.dom.DomHelper.prototype.createElement = function(name) {
  return goog.dom.createElement_(this.document_, name);
};
goog.dom.DomHelper.prototype.createTextNode = function(content) {
  return this.document_.createTextNode(String(content));
};
goog.dom.DomHelper.prototype.createTable = function(rows, columns, opt_fillWithNbsp) {
  return goog.dom.createTable_(this.document_, rows, columns, !!opt_fillWithNbsp);
};
goog.dom.DomHelper.prototype.safeHtmlToNode = function(html) {
  return goog.dom.safeHtmlToNode_(this.document_, html);
};
goog.dom.DomHelper.prototype.isCss1CompatMode = function() {
  return goog.dom.isCss1CompatMode_(this.document_);
};
goog.dom.DomHelper.prototype.getWindow = function() {
  return goog.dom.getWindow_(this.document_);
};
goog.dom.DomHelper.prototype.getDocumentScrollElement = function() {
  return goog.dom.getDocumentScrollElement_(this.document_);
};
goog.dom.DomHelper.prototype.getDocumentScroll = function() {
  return goog.dom.getDocumentScroll_(this.document_);
};
goog.dom.DomHelper.prototype.getActiveElement = function(opt_doc) {
  return goog.dom.getActiveElement(opt_doc || this.document_);
};
goog.dom.DomHelper.prototype.appendChild = goog.dom.appendChild;
goog.dom.DomHelper.prototype.append = goog.dom.append;
goog.dom.DomHelper.prototype.canHaveChildren = goog.dom.canHaveChildren;
goog.dom.DomHelper.prototype.removeChildren = goog.dom.removeChildren;
goog.dom.DomHelper.prototype.insertSiblingBefore = goog.dom.insertSiblingBefore;
goog.dom.DomHelper.prototype.insertSiblingAfter = goog.dom.insertSiblingAfter;
goog.dom.DomHelper.prototype.insertChildAt = goog.dom.insertChildAt;
goog.dom.DomHelper.prototype.removeNode = goog.dom.removeNode;
goog.dom.DomHelper.prototype.replaceNode = goog.dom.replaceNode;
goog.dom.DomHelper.prototype.copyContents = goog.dom.copyContents;
goog.dom.DomHelper.prototype.flattenElement = goog.dom.flattenElement;
goog.dom.DomHelper.prototype.getChildren = goog.dom.getChildren;
goog.dom.DomHelper.prototype.getFirstElementChild = goog.dom.getFirstElementChild;
goog.dom.DomHelper.prototype.getLastElementChild = goog.dom.getLastElementChild;
goog.dom.DomHelper.prototype.getNextElementSibling = goog.dom.getNextElementSibling;
goog.dom.DomHelper.prototype.getPreviousElementSibling = goog.dom.getPreviousElementSibling;
goog.dom.DomHelper.prototype.getNextNode = goog.dom.getNextNode;
goog.dom.DomHelper.prototype.getPreviousNode = goog.dom.getPreviousNode;
goog.dom.DomHelper.prototype.isNodeLike = goog.dom.isNodeLike;
goog.dom.DomHelper.prototype.isElement = goog.dom.isElement;
goog.dom.DomHelper.prototype.isWindow = goog.dom.isWindow;
goog.dom.DomHelper.prototype.getParentElement = goog.dom.getParentElement;
goog.dom.DomHelper.prototype.contains = goog.dom.contains;
goog.dom.DomHelper.prototype.compareNodeOrder = goog.dom.compareNodeOrder;
goog.dom.DomHelper.prototype.findCommonAncestor = goog.dom.findCommonAncestor;
goog.dom.DomHelper.prototype.getOwnerDocument = goog.dom.getOwnerDocument;
goog.dom.DomHelper.prototype.getFrameContentDocument = goog.dom.getFrameContentDocument;
goog.dom.DomHelper.prototype.getFrameContentWindow = goog.dom.getFrameContentWindow;
goog.dom.DomHelper.prototype.setTextContent = goog.dom.setTextContent;
goog.dom.DomHelper.prototype.getOuterHtml = goog.dom.getOuterHtml;
goog.dom.DomHelper.prototype.findNode = goog.dom.findNode;
goog.dom.DomHelper.prototype.findNodes = goog.dom.findNodes;
goog.dom.DomHelper.prototype.isFocusableTabIndex = goog.dom.isFocusableTabIndex;
goog.dom.DomHelper.prototype.setFocusableTabIndex = goog.dom.setFocusableTabIndex;
goog.dom.DomHelper.prototype.isFocusable = goog.dom.isFocusable;
goog.dom.DomHelper.prototype.getTextContent = goog.dom.getTextContent;
goog.dom.DomHelper.prototype.getNodeTextLength = goog.dom.getNodeTextLength;
goog.dom.DomHelper.prototype.getNodeTextOffset = goog.dom.getNodeTextOffset;
goog.dom.DomHelper.prototype.getNodeAtOffset = goog.dom.getNodeAtOffset;
goog.dom.DomHelper.prototype.isNodeList = goog.dom.isNodeList;
goog.dom.DomHelper.prototype.getAncestorByTagNameAndClass = goog.dom.getAncestorByTagNameAndClass;
goog.dom.DomHelper.prototype.getAncestorByClass = goog.dom.getAncestorByClass;
goog.dom.DomHelper.prototype.getAncestor = goog.dom.getAncestor;
goog.dom.DomHelper.prototype.getCanvasContext2D = goog.dom.getCanvasContext2D;
goog.async = {};
var module$contents$goog$async$FreeList_FreeList = function(create, reset, limit) {
  this.limit_ = limit;
  this.create_ = create;
  this.reset_ = reset;
  this.occupants_ = 0;
  this.head_ = null;
};
module$contents$goog$async$FreeList_FreeList.prototype.get = function() {
  if (0 < this.occupants_) {
    this.occupants_--;
    var item = this.head_;
    this.head_ = item.next;
    item.next = null;
  } else {
    item = this.create_();
  }
  return item;
};
module$contents$goog$async$FreeList_FreeList.prototype.put = function(item) {
  this.reset_(item);
  this.occupants_ < this.limit_ && (this.occupants_++, item.next = this.head_, this.head_ = item);
};
goog.async.FreeList = module$contents$goog$async$FreeList_FreeList;
goog.debug.entryPointRegistry = {};
goog.debug.entryPointRegistry.EntryPointMonitor = function() {
};
goog.debug.EntryPointMonitor = goog.debug.entryPointRegistry.EntryPointMonitor;
goog.debug.entryPointRegistry.refList_ = [];
goog.debug.entryPointRegistry.monitors_ = [];
goog.debug.entryPointRegistry.monitorsMayExist_ = !1;
goog.debug.entryPointRegistry.register = function(callback) {
  goog.debug.entryPointRegistry.refList_[goog.debug.entryPointRegistry.refList_.length] = callback;
  if (goog.debug.entryPointRegistry.monitorsMayExist_) {
    for (var monitors = goog.debug.entryPointRegistry.monitors_, i = 0; i < monitors.length; i++) {
      callback(goog.bind(monitors[i].wrap, monitors[i]));
    }
  }
};
goog.debug.entryPointRegistry.monitorAll = function(monitor) {
  goog.debug.entryPointRegistry.monitorsMayExist_ = !0;
  for (var transformer = goog.bind(monitor.wrap, monitor), i = 0; i < goog.debug.entryPointRegistry.refList_.length; i++) {
    goog.debug.entryPointRegistry.refList_[i](transformer);
  }
  goog.debug.entryPointRegistry.monitors_.push(monitor);
};
goog.debug.entryPointRegistry.unmonitorAllIfPossible = function(monitor) {
  var monitors = goog.debug.entryPointRegistry.monitors_;
  goog.asserts.assert(monitor == monitors[monitors.length - 1], "Only the most recent monitor can be unwrapped.");
  for (var transformer = goog.bind(monitor.unwrap, monitor), i = 0; i < goog.debug.entryPointRegistry.refList_.length; i++) {
    goog.debug.entryPointRegistry.refList_[i](transformer);
  }
  monitors.length--;
};
goog.async.nextTick = function(callback, opt_context, opt_useSetImmediate) {
  var cb = callback;
  opt_context && (cb = goog.bind(callback, opt_context));
  cb = goog.async.nextTick.wrapCallback_(cb);
  "function" === typeof goog.global.setImmediate && (opt_useSetImmediate || goog.async.nextTick.useSetImmediate_()) ? goog.global.setImmediate(cb) : (goog.async.nextTick.nextTickImpl || (goog.async.nextTick.nextTickImpl = goog.async.nextTick.getNextTickImpl_()), goog.async.nextTick.nextTickImpl(cb));
};
goog.async.nextTick.useSetImmediate_ = function() {
  return goog.global.Window && goog.global.Window.prototype && !module$contents$goog$labs$userAgent$browser_matchEdgeHtml() && goog.global.Window.prototype.setImmediate == goog.global.setImmediate ? !1 : !0;
};
goog.async.nextTick.getNextTickImpl_ = function() {
  var Channel = goog.global.MessageChannel;
  "undefined" === typeof Channel && "undefined" !== typeof window && window.postMessage && window.addEventListener && !module$contents$goog$labs$userAgent$engine_isPresto() && (Channel = function() {
    var iframe = goog.dom.createElement(goog.dom.TagName.IFRAME);
    iframe.style.display = "none";
    document.documentElement.appendChild(iframe);
    var win = iframe.contentWindow, doc = win.document;
    doc.open();
    doc.close();
    var message = "callImmediate" + Math.random(), origin = "file:" == win.location.protocol ? "*" : win.location.protocol + "//" + win.location.host, onmessage = goog.bind(function(e) {
      if (("*" == origin || e.origin == origin) && e.data == message) {
        this.port1.onmessage();
      }
    }, this);
    win.addEventListener("message", onmessage, !1);
    this.port1 = {};
    this.port2 = {postMessage:function() {
      win.postMessage(message, origin);
    }};
  });
  if ("undefined" !== typeof Channel && !module$contents$goog$labs$userAgent$browser_matchIE()) {
    var channel = new Channel(), head = {}, tail = head;
    channel.port1.onmessage = function() {
      if (void 0 !== head.next) {
        head = head.next;
        var cb = head.cb;
        head.cb = null;
        cb();
      }
    };
    return function(cb) {
      tail.next = {cb:cb};
      tail = tail.next;
      channel.port2.postMessage(0);
    };
  }
  return function(cb) {
    goog.global.setTimeout(cb, 0);
  };
};
goog.async.nextTick.wrapCallback_ = goog.functions.identity;
goog.debug.entryPointRegistry.register(function(transformer) {
  goog.async.nextTick.wrapCallback_ = transformer;
});
function module$contents$goog$async$throwException_throwException(exception) {
  goog.global.setTimeout(function() {
    throw exception;
  }, 0);
}
goog.async.throwException = module$contents$goog$async$throwException_throwException;
var module$contents$goog$async$WorkQueue_WorkQueue = function() {
  this.workTail_ = this.workHead_ = null;
};
module$contents$goog$async$WorkQueue_WorkQueue.prototype.add = function(fn, scope) {
  var item = this.getUnusedItem_();
  item.set(fn, scope);
  this.workTail_ ? this.workTail_.next = item : ((0,goog.asserts.assert)(!this.workHead_), this.workHead_ = item);
  this.workTail_ = item;
};
module$contents$goog$async$WorkQueue_WorkQueue.prototype.remove = function() {
  var item = null;
  this.workHead_ && (item = this.workHead_, this.workHead_ = this.workHead_.next, this.workHead_ || (this.workTail_ = null), item.next = null);
  return item;
};
module$contents$goog$async$WorkQueue_WorkQueue.prototype.returnUnused = function(item) {
  module$contents$goog$async$WorkQueue_WorkQueue.freelist_.put(item);
};
module$contents$goog$async$WorkQueue_WorkQueue.prototype.getUnusedItem_ = function() {
  return module$contents$goog$async$WorkQueue_WorkQueue.freelist_.get();
};
module$contents$goog$async$WorkQueue_WorkQueue.DEFAULT_MAX_UNUSED = 100;
module$contents$goog$async$WorkQueue_WorkQueue.freelist_ = new module$contents$goog$async$FreeList_FreeList(function() {
  return new module$contents$goog$async$WorkQueue_WorkItem();
}, function(item) {
  return item.reset();
}, module$contents$goog$async$WorkQueue_WorkQueue.DEFAULT_MAX_UNUSED);
var module$contents$goog$async$WorkQueue_WorkItem = function() {
  this.next = this.scope = this.fn = null;
};
module$contents$goog$async$WorkQueue_WorkItem.prototype.set = function(fn, scope) {
  this.fn = fn;
  this.scope = scope;
  this.next = null;
};
module$contents$goog$async$WorkQueue_WorkItem.prototype.reset = function() {
  this.next = this.scope = this.fn = null;
};
goog.async.WorkQueue = module$contents$goog$async$WorkQueue_WorkQueue;
goog.ASSUME_NATIVE_PROMISE = !1;
var module$contents$goog$async$run_schedule, module$contents$goog$async$run_workQueueScheduled = !1, module$contents$goog$async$run_workQueue = new module$contents$goog$async$WorkQueue_WorkQueue(), module$contents$goog$async$run_run = function(callback, context) {
  module$contents$goog$async$run_schedule || module$contents$goog$async$run_initializeRunner();
  module$contents$goog$async$run_workQueueScheduled || (module$contents$goog$async$run_schedule(), module$contents$goog$async$run_workQueueScheduled = !0);
  module$contents$goog$async$run_workQueue.add(callback, context);
}, module$contents$goog$async$run_initializeRunner = function() {
  if (goog.ASSUME_NATIVE_PROMISE || goog.global.Promise && goog.global.Promise.resolve) {
    var promise = goog.global.Promise.resolve(void 0);
    module$contents$goog$async$run_schedule = function() {
      promise.then(module$contents$goog$async$run_run.processWorkQueue);
    };
  } else {
    module$contents$goog$async$run_schedule = function() {
      (0,goog.async.nextTick)(module$contents$goog$async$run_run.processWorkQueue);
    };
  }
};
module$contents$goog$async$run_run.processWorkQueue = function() {
  for (var item; item = module$contents$goog$async$run_workQueue.remove();) {
    try {
      item.fn.call(item.scope);
    } catch (e) {
      module$contents$goog$async$throwException_throwException(e);
    }
    module$contents$goog$async$run_workQueue.returnUnused(item);
  }
  module$contents$goog$async$run_workQueueScheduled = !1;
};
goog.async.run = module$contents$goog$async$run_run;
goog.collections = {};
goog.collections.maps = {};
var module$contents$goog$collections$maps_MapLike = function() {
};
module$contents$goog$collections$maps_MapLike.prototype.set = function() {
};
module$contents$goog$collections$maps_MapLike.prototype.get = function() {
};
module$contents$goog$collections$maps_MapLike.prototype.keys = function() {
};
module$contents$goog$collections$maps_MapLike.prototype.values = function() {
};
module$contents$goog$collections$maps_MapLike.prototype.has = function() {
};
goog.collections.maps.MapLike = module$contents$goog$collections$maps_MapLike;
function module$contents$goog$collections$maps_setAll(map, entries) {
  if (entries) {
    for (var $jscomp$iter$0 = $jscomp.makeIterator(entries), $jscomp$key$ = $jscomp$iter$0.next(); !$jscomp$key$.done; $jscomp$key$ = $jscomp$iter$0.next()) {
      var $jscomp$destructuring$var12 = $jscomp$key$.value, $jscomp$destructuring$var13 = $jscomp.makeIterator($jscomp$destructuring$var12), k = $jscomp$destructuring$var13.next().value, v = $jscomp$destructuring$var13.next().value;
      map.set(k, v);
    }
  }
}
goog.collections.maps.setAll = module$contents$goog$collections$maps_setAll;
function module$contents$goog$collections$maps_hasValue(map, val, valueEqualityFn) {
  valueEqualityFn = void 0 === valueEqualityFn ? module$contents$goog$collections$maps_defaultEqualityFn : valueEqualityFn;
  for (var $jscomp$iter$1 = $jscomp.makeIterator(map.values()), $jscomp$key$v = $jscomp$iter$1.next(); !$jscomp$key$v.done; $jscomp$key$v = $jscomp$iter$1.next()) {
    var v = $jscomp$key$v.value;
    if (valueEqualityFn(v, val)) {
      return !0;
    }
  }
  return !1;
}
goog.collections.maps.hasValue = module$contents$goog$collections$maps_hasValue;
var module$contents$goog$collections$maps_defaultEqualityFn = function(a, b) {
  return a === b;
};
function module$contents$goog$collections$maps_equals(map, otherMap, valueEqualityFn) {
  valueEqualityFn = void 0 === valueEqualityFn ? module$contents$goog$collections$maps_defaultEqualityFn : valueEqualityFn;
  if (map === otherMap) {
    return !0;
  }
  if (map.size !== otherMap.size) {
    return !1;
  }
  for (var $jscomp$iter$2 = $jscomp.makeIterator(map.keys()), $jscomp$key$key = $jscomp$iter$2.next(); !$jscomp$key$key.done; $jscomp$key$key = $jscomp$iter$2.next()) {
    var key = $jscomp$key$key.value;
    if (!otherMap.has(key) || !valueEqualityFn(map.get(key), otherMap.get(key))) {
      return !1;
    }
  }
  return !0;
}
goog.collections.maps.equals = module$contents$goog$collections$maps_equals;
function module$contents$goog$collections$maps_transpose(map) {
  for (var transposed = new Map(), $jscomp$iter$3 = $jscomp.makeIterator(map.keys()), $jscomp$key$key = $jscomp$iter$3.next(); !$jscomp$key$key.done; $jscomp$key$key = $jscomp$iter$3.next()) {
    var key = $jscomp$key$key.value, val = map.get(key);
    transposed.set(val, key);
  }
  return transposed;
}
goog.collections.maps.transpose = module$contents$goog$collections$maps_transpose;
function module$contents$goog$collections$maps_toObject(map) {
  for (var obj = {}, $jscomp$iter$4 = $jscomp.makeIterator(map.keys()), $jscomp$key$key = $jscomp$iter$4.next(); !$jscomp$key$key.done; $jscomp$key$key = $jscomp$iter$4.next()) {
    var key = $jscomp$key$key.value;
    obj[key] = map.get(key);
  }
  return obj;
}
goog.collections.maps.toObject = module$contents$goog$collections$maps_toObject;
goog.debug.errorcontext = {};
goog.debug.errorcontext.addErrorContext = function(err, contextKey, contextValue) {
  err[goog.debug.errorcontext.CONTEXT_KEY_] || (err[goog.debug.errorcontext.CONTEXT_KEY_] = {});
  err[goog.debug.errorcontext.CONTEXT_KEY_][contextKey] = contextValue;
};
goog.debug.errorcontext.getErrorContext = function(err) {
  return err[goog.debug.errorcontext.CONTEXT_KEY_] || {};
};
goog.debug.errorcontext.CONTEXT_KEY_ = "__closure__error__context__984382";
goog.debug.LOGGING_ENABLED = goog.DEBUG;
goog.debug.FORCE_SLOPPY_STACKS = !1;
goog.debug.CHECK_FOR_THROWN_EVENT = !1;
goog.debug.catchErrors = function(logFunc, opt_cancel, opt_target) {
  var target = opt_target || goog.global, oldErrorHandler = target.onerror, retVal = !!opt_cancel;
  target.onerror = function(message, url, line, opt_col, opt_error) {
    oldErrorHandler && oldErrorHandler(message, url, line, opt_col, opt_error);
    logFunc({message:message, fileName:url, line:line, lineNumber:line, col:opt_col, error:opt_error});
    return retVal;
  };
};
goog.debug.expose = function(obj, opt_showFn) {
  if ("undefined" == typeof obj) {
    return "undefined";
  }
  if (null == obj) {
    return "NULL";
  }
  var str = [], x;
  for (x in obj) {
    if (opt_showFn || "function" !== typeof obj[x]) {
      var s = x + " = ";
      try {
        s += obj[x];
      } catch (e) {
        s += "*** " + e + " ***";
      }
      str.push(s);
    }
  }
  return str.join("\n");
};
goog.debug.deepExpose = function(obj$jscomp$0, opt_showFn) {
  var str = [], uidsToCleanup = [], ancestorUids = {}, helper = function(obj, space) {
    var nestspace = space + "  ";
    try {
      if (void 0 === obj) {
        str.push("undefined");
      } else if (null === obj) {
        str.push("NULL");
      } else if ("string" === typeof obj) {
        str.push('"' + obj.replace(/\n/g, "\n" + space) + '"');
      } else if ("function" === typeof obj) {
        str.push(String(obj).replace(/\n/g, "\n" + space));
      } else if (goog.isObject(obj)) {
        goog.hasUid(obj) || uidsToCleanup.push(obj);
        var uid = goog.getUid(obj);
        if (ancestorUids[uid]) {
          str.push("*** reference loop detected (id=" + uid + ") ***");
        } else {
          ancestorUids[uid] = !0;
          str.push("{");
          for (var x in obj) {
            if (opt_showFn || "function" !== typeof obj[x]) {
              str.push("\n"), str.push(nestspace), str.push(x + " = "), helper(obj[x], nestspace);
            }
          }
          str.push("\n" + space + "}");
          delete ancestorUids[uid];
        }
      } else {
        str.push(obj);
      }
    } catch (e) {
      str.push("*** " + e + " ***");
    }
  };
  helper(obj$jscomp$0, "");
  for (var i = 0; i < uidsToCleanup.length; i++) {
    goog.removeUid(uidsToCleanup[i]);
  }
  return str.join("");
};
goog.debug.exposeArray = function(arr) {
  for (var str = [], i = 0; i < arr.length; i++) {
    Array.isArray(arr[i]) ? str.push(goog.debug.exposeArray(arr[i])) : str.push(arr[i]);
  }
  return "[ " + str.join(", ") + " ]";
};
goog.debug.normalizeErrorObject = function(err) {
  var href = goog.getObjectByName("window.location.href");
  null == err && (err = 'Unknown Error of type "null/undefined"');
  if ("string" === typeof err) {
    return {message:err, name:"Unknown error", lineNumber:"Not available", fileName:href, stack:"Not available"};
  }
  var threwError = !1;
  try {
    var lineNumber = err.lineNumber || err.line || "Not available";
  } catch (e) {
    lineNumber = "Not available", threwError = !0;
  }
  try {
    var fileName = err.fileName || err.filename || err.sourceURL || goog.global.$googDebugFname || href;
  } catch (e$20) {
    fileName = "Not available", threwError = !0;
  }
  var stack = goog.debug.serializeErrorStack_(err);
  if (!(!threwError && err.lineNumber && err.fileName && err.stack && err.message && err.name)) {
    var message = err.message;
    if (null == message) {
      if (err.constructor && err.constructor instanceof Function) {
        var ctorName = err.constructor.name ? err.constructor.name : goog.debug.getFunctionName(err.constructor);
        message = 'Unknown Error of type "' + ctorName + '"';
        if (goog.debug.CHECK_FOR_THROWN_EVENT && "Event" == ctorName) {
          try {
            message = message + ' with Event.type "' + (err.type || "") + '"';
          } catch (e$21) {
          }
        }
      } else {
        message = "Unknown Error of unknown type";
      }
      "function" === typeof err.toString && Object.prototype.toString !== err.toString && (message += ": " + err.toString());
    }
    return {message:message, name:err.name || "UnknownError", lineNumber:lineNumber, fileName:fileName, stack:stack || "Not available"};
  }
  err.stack = stack;
  return {message:err.message, name:err.name, lineNumber:err.lineNumber, fileName:err.fileName, stack:err.stack};
};
goog.debug.serializeErrorStack_ = function(e, seen) {
  seen || (seen = {});
  seen[goog.debug.serializeErrorAsKey_(e)] = !0;
  var stack = e.stack || "", cause = e.cause;
  cause && !seen[goog.debug.serializeErrorAsKey_(cause)] && (stack += "\nCaused by: ", cause.stack && 0 == cause.stack.indexOf(cause.toString()) || (stack += "string" === typeof cause ? cause : cause.message + "\n"), stack += goog.debug.serializeErrorStack_(cause, seen));
  return stack;
};
goog.debug.serializeErrorAsKey_ = function(e) {
  var keyPrefix = "";
  "function" === typeof e.toString && (keyPrefix = "" + e);
  return keyPrefix + e.stack;
};
goog.debug.enhanceError = function(err, opt_message) {
  if (err instanceof Error) {
    var error = err;
  } else {
    error = Error(err), Error.captureStackTrace && Error.captureStackTrace(error, goog.debug.enhanceError);
  }
  error.stack || (error.stack = goog.debug.getStacktrace(goog.debug.enhanceError));
  if (opt_message) {
    for (var x = 0; error["message" + x];) {
      ++x;
    }
    error["message" + x] = String(opt_message);
  }
  return error;
};
goog.debug.enhanceErrorWithContext = function(err, opt_context) {
  var error = goog.debug.enhanceError(err);
  if (opt_context) {
    for (var key in opt_context) {
      goog.debug.errorcontext.addErrorContext(error, key, opt_context[key]);
    }
  }
  return error;
};
goog.debug.getStacktraceSimple = function(opt_depth) {
  if (!goog.debug.FORCE_SLOPPY_STACKS) {
    var stack = goog.debug.getNativeStackTrace_(goog.debug.getStacktraceSimple);
    if (stack) {
      return stack;
    }
  }
  for (var sb = [], fn = arguments.callee.caller, depth = 0; fn && (!opt_depth || depth < opt_depth);) {
    sb.push(goog.debug.getFunctionName(fn));
    sb.push("()\n");
    try {
      fn = fn.caller;
    } catch (e) {
      sb.push("[exception trying to get caller]\n");
      break;
    }
    depth++;
    if (depth >= goog.debug.MAX_STACK_DEPTH) {
      sb.push("[...long stack...]");
      break;
    }
  }
  opt_depth && depth >= opt_depth ? sb.push("[...reached max depth limit...]") : sb.push("[end]");
  return sb.join("");
};
goog.debug.MAX_STACK_DEPTH = 50;
goog.debug.getNativeStackTrace_ = function(fn) {
  var tempErr = Error();
  if (Error.captureStackTrace) {
    return Error.captureStackTrace(tempErr, fn), String(tempErr.stack);
  }
  try {
    throw tempErr;
  } catch (e) {
    tempErr = e;
  }
  var stack = tempErr.stack;
  return stack ? String(stack) : null;
};
goog.debug.getStacktrace = function(fn) {
  if (!goog.debug.FORCE_SLOPPY_STACKS) {
    var contextFn = fn || goog.debug.getStacktrace;
    var stack = goog.debug.getNativeStackTrace_(contextFn);
  }
  stack || (stack = goog.debug.getStacktraceHelper_(fn || arguments.callee.caller, []));
  return stack;
};
goog.debug.getStacktraceHelper_ = function(fn, visited) {
  var sb = [];
  if (module$contents$goog$array_contains(visited, fn)) {
    sb.push("[...circular reference...]");
  } else if (fn && visited.length < goog.debug.MAX_STACK_DEPTH) {
    sb.push(goog.debug.getFunctionName(fn) + "(");
    for (var args = fn.arguments, i = 0; args && i < args.length; i++) {
      0 < i && sb.push(", ");
      var arg = args[i];
      switch(typeof arg) {
        case "object":
          var argDesc = arg ? "object" : "null";
          break;
        case "string":
          argDesc = arg;
          break;
        case "number":
          argDesc = String(arg);
          break;
        case "boolean":
          argDesc = arg ? "true" : "false";
          break;
        case "function":
          argDesc = (argDesc = goog.debug.getFunctionName(arg)) ? argDesc : "[fn]";
          break;
        default:
          argDesc = typeof arg;
      }
      40 < argDesc.length && (argDesc = argDesc.slice(0, 40) + "...");
      sb.push(argDesc);
    }
    visited.push(fn);
    sb.push(")\n");
    try {
      sb.push(goog.debug.getStacktraceHelper_(fn.caller, visited));
    } catch (e) {
      sb.push("[exception trying to get caller]\n");
    }
  } else {
    fn ? sb.push("[...long stack...]") : sb.push("[end]");
  }
  return sb.join("");
};
goog.debug.getFunctionName = function(fn) {
  if (goog.debug.fnNameCache_[fn]) {
    return goog.debug.fnNameCache_[fn];
  }
  var functionSource = String(fn);
  if (!goog.debug.fnNameCache_[functionSource]) {
    var matches = /function\s+([^\(]+)/m.exec(functionSource);
    if (matches) {
      var method = matches[1];
      goog.debug.fnNameCache_[functionSource] = method;
    } else {
      goog.debug.fnNameCache_[functionSource] = "[Anonymous]";
    }
  }
  return goog.debug.fnNameCache_[functionSource];
};
goog.debug.makeWhitespaceVisible = function(string) {
  return string.replace(/ /g, "[_]").replace(/\f/g, "[f]").replace(/\n/g, "[n]\n").replace(/\r/g, "[r]").replace(/\t/g, "[t]");
};
goog.debug.runtimeType = function(value) {
  return value instanceof Function ? value.displayName || value.name || "unknown type name" : value instanceof Object ? value.constructor.displayName || value.constructor.name || Object.prototype.toString.call(value) : null === value ? "null" : typeof value;
};
goog.debug.fnNameCache_ = {};
goog.debug.freezeInternal_ = goog.DEBUG && Object.freeze || function(arg) {
  return arg;
};
goog.debug.freeze = function(arg) {
  return goog.debug.freezeInternal_(arg);
};
function module$contents$goog$dispose_dispose(obj) {
  obj && "function" == typeof obj.dispose && obj.dispose();
}
goog.dispose = module$contents$goog$dispose_dispose;
function module$contents$goog$disposeAll_disposeAll(var_args) {
  for (var i = 0, len = arguments.length; i < len; ++i) {
    var disposable = arguments[i];
    goog.isArrayLike(disposable) ? module$contents$goog$disposeAll_disposeAll.apply(null, disposable) : module$contents$goog$dispose_dispose(disposable);
  }
}
goog.disposeAll = module$contents$goog$disposeAll_disposeAll;
goog.disposable = {};
goog.disposable.IDisposable = function() {
};
goog.Disposable = function() {
  goog.Disposable.MONITORING_MODE != goog.Disposable.MonitoringMode.OFF && (goog.Disposable.instances_[goog.getUid(this)] = this);
  this.disposed_ = this.disposed_;
  this.onDisposeCallbacks_ = this.onDisposeCallbacks_;
};
goog.Disposable.MonitoringMode = {OFF:0, PERMANENT:1, INTERACTIVE:2};
goog.Disposable.MONITORING_MODE = 0;
goog.Disposable.INCLUDE_STACK_ON_CREATION = !0;
goog.Disposable.instances_ = {};
goog.Disposable.getUndisposedObjects = function() {
  var ret = [], id;
  for (id in goog.Disposable.instances_) {
    goog.Disposable.instances_.hasOwnProperty(id) && ret.push(goog.Disposable.instances_[Number(id)]);
  }
  return ret;
};
goog.Disposable.clearUndisposedObjects = function() {
  goog.Disposable.instances_ = {};
};
goog.Disposable.prototype.disposed_ = !1;
goog.Disposable.prototype.isDisposed = function() {
  return this.disposed_;
};
goog.Disposable.prototype.dispose = function() {
  if (!this.disposed_ && (this.disposed_ = !0, this.disposeInternal(), goog.Disposable.MONITORING_MODE != goog.Disposable.MonitoringMode.OFF)) {
    var uid = goog.getUid(this);
    if (goog.Disposable.MONITORING_MODE == goog.Disposable.MonitoringMode.PERMANENT && !goog.Disposable.instances_.hasOwnProperty(uid)) {
      throw Error(this + " did not call the goog.Disposable base constructor or was disposed of after a clearUndisposedObjects call");
    }
    if (goog.Disposable.MONITORING_MODE != goog.Disposable.MonitoringMode.OFF && this.onDisposeCallbacks_ && 0 < this.onDisposeCallbacks_.length) {
      throw Error(this + " did not empty its onDisposeCallbacks queue. This probably means it overrode dispose() or disposeInternal() without calling the superclass' method.");
    }
    delete goog.Disposable.instances_[uid];
  }
};
goog.Disposable.prototype.disposeInternal = function() {
  if (this.onDisposeCallbacks_) {
    for (; this.onDisposeCallbacks_.length;) {
      this.onDisposeCallbacks_.shift()();
    }
  }
};
goog.Disposable.isDisposed = function(obj) {
  return obj && "function" == typeof obj.isDisposed ? obj.isDisposed() : !1;
};
goog.events = {};
goog.events.EventId = function(eventId) {
  this.id = eventId;
};
goog.events.EventId.prototype.toString = function() {
  return this.id;
};
goog.events.Event = function(type, opt_target) {
  this.type = type instanceof goog.events.EventId ? String(type) : type;
  this.currentTarget = this.target = opt_target;
  this.defaultPrevented = this.propagationStopped_ = !1;
};
goog.events.Event.prototype.stopPropagation = function() {
  this.propagationStopped_ = !0;
};
goog.events.Event.prototype.preventDefault = function() {
  this.defaultPrevented = !0;
};
goog.events.Event.stopPropagation = function(e) {
  e.stopPropagation();
};
goog.events.Event.preventDefault = function(e) {
  e.preventDefault();
};
goog.events.BrowserFeature = {TOUCH_ENABLED:"ontouchstart" in goog.global || !!(goog.global.document && document.documentElement && "ontouchstart" in document.documentElement) || !(!goog.global.navigator || !goog.global.navigator.maxTouchPoints && !goog.global.navigator.msMaxTouchPoints), POINTER_EVENTS:"PointerEvent" in goog.global, MSPOINTER_EVENTS:"MSPointerEvent" in goog.global && !(!goog.global.navigator || !goog.global.navigator.msPointerEnabled), PASSIVE_EVENTS:function() {
  if (!goog.global.addEventListener || !Object.defineProperty) {
    return !1;
  }
  var passive = !1, options = Object.defineProperty({}, "passive", {get:function() {
    passive = !0;
  }});
  try {
    goog.global.addEventListener("test", function() {
    }, options), goog.global.removeEventListener("test", function() {
    }, options);
  } catch (e) {
  }
  return passive;
}()};
goog.events.eventTypeHelpers = {};
goog.events.eventTypeHelpers.getVendorPrefixedName = function(eventName) {
  return goog.userAgent.WEBKIT ? "webkit" + eventName : eventName.toLowerCase();
};
goog.events.eventTypeHelpers.getPointerFallbackEventName = function(pointerEventName, msPointerEventName, fallbackEventName) {
  return goog.events.BrowserFeature.POINTER_EVENTS ? pointerEventName : goog.events.BrowserFeature.MSPOINTER_EVENTS ? msPointerEventName : fallbackEventName;
};
goog.events.EventType = {CLICK:"click", RIGHTCLICK:"rightclick", DBLCLICK:"dblclick", AUXCLICK:"auxclick", MOUSEDOWN:"mousedown", MOUSEUP:"mouseup", MOUSEOVER:"mouseover", MOUSEOUT:"mouseout", MOUSEMOVE:"mousemove", MOUSEENTER:"mouseenter", MOUSELEAVE:"mouseleave", MOUSECANCEL:"mousecancel", SELECTIONCHANGE:"selectionchange", SELECTSTART:"selectstart", WHEEL:"wheel", KEYPRESS:"keypress", KEYDOWN:"keydown", KEYUP:"keyup", BLUR:"blur", FOCUS:"focus", DEACTIVATE:"deactivate", FOCUSIN:"focusin", FOCUSOUT:"focusout", 
CHANGE:"change", RESET:"reset", SELECT:"select", SUBMIT:"submit", INPUT:"input", PROPERTYCHANGE:"propertychange", DRAGSTART:"dragstart", DRAG:"drag", DRAGENTER:"dragenter", DRAGOVER:"dragover", DRAGLEAVE:"dragleave", DROP:"drop", DRAGEND:"dragend", TOUCHSTART:"touchstart", TOUCHMOVE:"touchmove", TOUCHEND:"touchend", TOUCHCANCEL:"touchcancel", BEFOREUNLOAD:"beforeunload", CONSOLEMESSAGE:"consolemessage", CONTEXTMENU:"contextmenu", DEVICECHANGE:"devicechange", DEVICEMOTION:"devicemotion", DEVICEORIENTATION:"deviceorientation", 
DOMCONTENTLOADED:"DOMContentLoaded", ERROR:"error", HELP:"help", LOAD:"load", LOSECAPTURE:"losecapture", ORIENTATIONCHANGE:"orientationchange", READYSTATECHANGE:"readystatechange", RESIZE:"resize", SCROLL:"scroll", UNLOAD:"unload", CANPLAY:"canplay", CANPLAYTHROUGH:"canplaythrough", DURATIONCHANGE:"durationchange", EMPTIED:"emptied", ENDED:"ended", LOADEDDATA:"loadeddata", LOADEDMETADATA:"loadedmetadata", PAUSE:"pause", PLAY:"play", PLAYING:"playing", PROGRESS:"progress", RATECHANGE:"ratechange", 
SEEKED:"seeked", SEEKING:"seeking", STALLED:"stalled", SUSPEND:"suspend", TIMEUPDATE:"timeupdate", VOLUMECHANGE:"volumechange", WAITING:"waiting", SOURCEOPEN:"sourceopen", SOURCEENDED:"sourceended", SOURCECLOSED:"sourceclosed", ABORT:"abort", UPDATE:"update", UPDATESTART:"updatestart", UPDATEEND:"updateend", HASHCHANGE:"hashchange", PAGEHIDE:"pagehide", PAGESHOW:"pageshow", POPSTATE:"popstate", COPY:"copy", PASTE:"paste", CUT:"cut", BEFORECOPY:"beforecopy", BEFORECUT:"beforecut", BEFOREPASTE:"beforepaste", 
ONLINE:"online", OFFLINE:"offline", MESSAGE:"message", CONNECT:"connect", INSTALL:"install", ACTIVATE:"activate", FETCH:"fetch", FOREIGNFETCH:"foreignfetch", MESSAGEERROR:"messageerror", STATECHANGE:"statechange", UPDATEFOUND:"updatefound", CONTROLLERCHANGE:"controllerchange", ANIMATIONSTART:goog.events.eventTypeHelpers.getVendorPrefixedName("AnimationStart"), ANIMATIONEND:goog.events.eventTypeHelpers.getVendorPrefixedName("AnimationEnd"), ANIMATIONITERATION:goog.events.eventTypeHelpers.getVendorPrefixedName("AnimationIteration"), 
TRANSITIONEND:goog.events.eventTypeHelpers.getVendorPrefixedName("TransitionEnd"), POINTERDOWN:"pointerdown", POINTERUP:"pointerup", POINTERCANCEL:"pointercancel", POINTERMOVE:"pointermove", POINTEROVER:"pointerover", POINTEROUT:"pointerout", POINTERENTER:"pointerenter", POINTERLEAVE:"pointerleave", GOTPOINTERCAPTURE:"gotpointercapture", LOSTPOINTERCAPTURE:"lostpointercapture", MSGESTURECHANGE:"MSGestureChange", MSGESTUREEND:"MSGestureEnd", MSGESTUREHOLD:"MSGestureHold", MSGESTURESTART:"MSGestureStart", 
MSGESTURETAP:"MSGestureTap", MSGOTPOINTERCAPTURE:"MSGotPointerCapture", MSINERTIASTART:"MSInertiaStart", MSLOSTPOINTERCAPTURE:"MSLostPointerCapture", MSPOINTERCANCEL:"MSPointerCancel", MSPOINTERDOWN:"MSPointerDown", MSPOINTERENTER:"MSPointerEnter", MSPOINTERHOVER:"MSPointerHover", MSPOINTERLEAVE:"MSPointerLeave", MSPOINTERMOVE:"MSPointerMove", MSPOINTEROUT:"MSPointerOut", MSPOINTEROVER:"MSPointerOver", MSPOINTERUP:"MSPointerUp", TEXT:"text", TEXTINPUT:goog.userAgent.IE ? "textinput" : "textInput", 
COMPOSITIONSTART:"compositionstart", COMPOSITIONUPDATE:"compositionupdate", COMPOSITIONEND:"compositionend", BEFOREINPUT:"beforeinput", EXIT:"exit", LOADABORT:"loadabort", LOADCOMMIT:"loadcommit", LOADREDIRECT:"loadredirect", LOADSTART:"loadstart", LOADSTOP:"loadstop", RESPONSIVE:"responsive", SIZECHANGED:"sizechanged", UNRESPONSIVE:"unresponsive", VISIBILITYCHANGE:"visibilitychange", STORAGE:"storage", DOMSUBTREEMODIFIED:"DOMSubtreeModified", DOMNODEINSERTED:"DOMNodeInserted", DOMNODEREMOVED:"DOMNodeRemoved", 
DOMNODEREMOVEDFROMDOCUMENT:"DOMNodeRemovedFromDocument", DOMNODEINSERTEDINTODOCUMENT:"DOMNodeInsertedIntoDocument", DOMATTRMODIFIED:"DOMAttrModified", DOMCHARACTERDATAMODIFIED:"DOMCharacterDataModified", BEFOREPRINT:"beforeprint", AFTERPRINT:"afterprint", BEFOREINSTALLPROMPT:"beforeinstallprompt", APPINSTALLED:"appinstalled", CANCEL:"cancel", FINISH:"finish", REMOVE:"remove"};
goog.events.BrowserEvent = function(opt_e, opt_currentTarget) {
  goog.events.Event.call(this, opt_e ? opt_e.type : "");
  this.relatedTarget = this.currentTarget = this.target = null;
  this.button = this.screenY = this.screenX = this.clientY = this.clientX = this.offsetY = this.offsetX = 0;
  this.key = "";
  this.charCode = this.keyCode = 0;
  this.metaKey = this.shiftKey = this.altKey = this.ctrlKey = !1;
  this.state = null;
  this.pointerId = 0;
  this.pointerType = "";
  this.event_ = null;
  opt_e && this.init(opt_e, opt_currentTarget);
};
goog.inherits(goog.events.BrowserEvent, goog.events.Event);
goog.events.BrowserEvent.USE_LAYER_XY_AS_OFFSET_XY = !1;
goog.events.BrowserEvent.MouseButton = {LEFT:0, MIDDLE:1, RIGHT:2, BACK:3, FORWARD:4,};
goog.events.BrowserEvent.PointerType = {MOUSE:"mouse", PEN:"pen", TOUCH:"touch"};
goog.events.BrowserEvent.IEButtonMap = goog.debug.freeze([1, 4, 2]);
goog.events.BrowserEvent.IE_BUTTON_MAP = goog.events.BrowserEvent.IEButtonMap;
goog.events.BrowserEvent.IE_POINTER_TYPE_MAP = goog.debug.freeze({2:goog.events.BrowserEvent.PointerType.TOUCH, 3:goog.events.BrowserEvent.PointerType.PEN, 4:goog.events.BrowserEvent.PointerType.MOUSE});
goog.events.BrowserEvent.prototype.init = function(e, opt_currentTarget) {
  var type = this.type = e.type, relevantTouch = e.changedTouches && e.changedTouches.length ? e.changedTouches[0] : null;
  this.target = e.target || e.srcElement;
  this.currentTarget = opt_currentTarget;
  var relatedTarget = e.relatedTarget;
  relatedTarget ? goog.userAgent.GECKO && (goog.reflect.canAccessProperty(relatedTarget, "nodeName") || (relatedTarget = null)) : type == goog.events.EventType.MOUSEOVER ? relatedTarget = e.fromElement : type == goog.events.EventType.MOUSEOUT && (relatedTarget = e.toElement);
  this.relatedTarget = relatedTarget;
  relevantTouch ? (this.clientX = void 0 !== relevantTouch.clientX ? relevantTouch.clientX : relevantTouch.pageX, this.clientY = void 0 !== relevantTouch.clientY ? relevantTouch.clientY : relevantTouch.pageY, this.screenX = relevantTouch.screenX || 0, this.screenY = relevantTouch.screenY || 0) : (goog.events.BrowserEvent.USE_LAYER_XY_AS_OFFSET_XY ? (this.offsetX = void 0 !== e.layerX ? e.layerX : e.offsetX, this.offsetY = void 0 !== e.layerY ? e.layerY : e.offsetY) : (this.offsetX = goog.userAgent.WEBKIT || 
  void 0 !== e.offsetX ? e.offsetX : e.layerX, this.offsetY = goog.userAgent.WEBKIT || void 0 !== e.offsetY ? e.offsetY : e.layerY), this.clientX = void 0 !== e.clientX ? e.clientX : e.pageX, this.clientY = void 0 !== e.clientY ? e.clientY : e.pageY, this.screenX = e.screenX || 0, this.screenY = e.screenY || 0);
  this.button = e.button;
  this.keyCode = e.keyCode || 0;
  this.key = e.key || "";
  this.charCode = e.charCode || ("keypress" == type ? e.keyCode : 0);
  this.ctrlKey = e.ctrlKey;
  this.altKey = e.altKey;
  this.shiftKey = e.shiftKey;
  this.metaKey = e.metaKey;
  this.pointerId = e.pointerId || 0;
  this.pointerType = goog.events.BrowserEvent.getPointerType_(e);
  this.state = e.state;
  this.event_ = e;
  e.defaultPrevented && goog.events.BrowserEvent.superClass_.preventDefault.call(this);
};
goog.events.BrowserEvent.prototype.stopPropagation = function() {
  goog.events.BrowserEvent.superClass_.stopPropagation.call(this);
  this.event_.stopPropagation ? this.event_.stopPropagation() : this.event_.cancelBubble = !0;
};
goog.events.BrowserEvent.prototype.preventDefault = function() {
  goog.events.BrowserEvent.superClass_.preventDefault.call(this);
  var be = this.event_;
  be.preventDefault ? be.preventDefault() : be.returnValue = !1;
};
goog.events.BrowserEvent.getPointerType_ = function(e) {
  return "string" === typeof e.pointerType ? e.pointerType : goog.events.BrowserEvent.IE_POINTER_TYPE_MAP[e.pointerType] || "";
};
goog.events.Listenable = function() {
};
goog.events.Listenable.IMPLEMENTED_BY_PROP = "closure_listenable_" + (1E6 * Math.random() | 0);
goog.events.Listenable.addImplementation = function(cls) {
  cls.prototype[goog.events.Listenable.IMPLEMENTED_BY_PROP] = !0;
};
goog.events.Listenable.isImplementedBy = function(obj) {
  return !(!obj || !obj[goog.events.Listenable.IMPLEMENTED_BY_PROP]);
};
goog.events.Listenable.prototype.listen = function() {
};
goog.events.Listenable.prototype.listenOnce = function() {
};
goog.events.Listenable.prototype.unlisten = function() {
};
goog.events.Listenable.prototype.unlistenByKey = function() {
};
goog.events.Listenable.prototype.dispatchEvent = function() {
};
goog.events.Listenable.prototype.removeAllListeners = function() {
};
goog.events.Listenable.prototype.getParentEventTarget = function() {
};
goog.events.Listenable.prototype.fireListeners = function() {
};
goog.events.Listenable.prototype.getListeners = function() {
};
goog.events.Listenable.prototype.getListener = function() {
};
goog.events.Listenable.prototype.hasListener = function() {
};
goog.events.ListenableKey = function() {
};
goog.events.ListenableKey.counter_ = 0;
goog.events.ListenableKey.reserveKey = function() {
  return ++goog.events.ListenableKey.counter_;
};
goog.events.Listener = function(listener, proxy, src, type, capture, opt_handler) {
  this.listener = listener;
  this.proxy = proxy;
  this.src = src;
  this.type = type;
  this.capture = !!capture;
  this.handler = opt_handler;
  this.key = goog.events.ListenableKey.reserveKey();
  this.removed = this.callOnce = !1;
};
goog.events.Listener.ENABLE_MONITORING = !1;
goog.events.Listener.prototype.markAsRemoved = function() {
  this.removed = !0;
  this.handler = this.src = this.proxy = this.listener = null;
};
goog.events.ListenerMap = function(src) {
  this.src = src;
  this.listeners = {};
  this.typeCount_ = 0;
};
goog.events.ListenerMap.prototype.add = function(type, listener, callOnce, opt_useCapture, opt_listenerScope) {
  var typeStr = type.toString(), listenerArray = this.listeners[typeStr];
  listenerArray || (listenerArray = this.listeners[typeStr] = [], this.typeCount_++);
  var index = goog.events.ListenerMap.findListenerIndex_(listenerArray, listener, opt_useCapture, opt_listenerScope);
  if (-1 < index) {
    var listenerObj = listenerArray[index];
    callOnce || (listenerObj.callOnce = !1);
  } else {
    listenerObj = new goog.events.Listener(listener, null, this.src, typeStr, !!opt_useCapture, opt_listenerScope), listenerObj.callOnce = callOnce, listenerArray.push(listenerObj);
  }
  return listenerObj;
};
goog.events.ListenerMap.prototype.remove = function(type, listener, opt_useCapture, opt_listenerScope) {
  var typeStr = type.toString();
  if (!(typeStr in this.listeners)) {
    return !1;
  }
  var listenerArray = this.listeners[typeStr], index = goog.events.ListenerMap.findListenerIndex_(listenerArray, listener, opt_useCapture, opt_listenerScope);
  if (-1 < index) {
    var listenerObj = listenerArray[index];
    listenerObj.markAsRemoved();
    module$contents$goog$array_removeAt(listenerArray, index);
    0 == listenerArray.length && (delete this.listeners[typeStr], this.typeCount_--);
    return !0;
  }
  return !1;
};
goog.events.ListenerMap.prototype.removeByKey = function(listener) {
  var type = listener.type;
  if (!(type in this.listeners)) {
    return !1;
  }
  var removed = module$contents$goog$array_remove(this.listeners[type], listener);
  removed && (listener.markAsRemoved(), 0 == this.listeners[type].length && (delete this.listeners[type], this.typeCount_--));
  return removed;
};
goog.events.ListenerMap.prototype.removeAll = function(opt_type) {
  var typeStr = opt_type && opt_type.toString(), count = 0, type;
  for (type in this.listeners) {
    if (!typeStr || type == typeStr) {
      for (var listenerArray = this.listeners[type], i = 0; i < listenerArray.length; i++) {
        ++count, listenerArray[i].markAsRemoved();
      }
      delete this.listeners[type];
      this.typeCount_--;
    }
  }
  return count;
};
goog.events.ListenerMap.prototype.getListeners = function(type, capture) {
  var listenerArray = this.listeners[type.toString()], rv = [];
  if (listenerArray) {
    for (var i = 0; i < listenerArray.length; ++i) {
      var listenerObj = listenerArray[i];
      listenerObj.capture == capture && rv.push(listenerObj);
    }
  }
  return rv;
};
goog.events.ListenerMap.prototype.getListener = function(type, listener, capture, opt_listenerScope) {
  var listenerArray = this.listeners[type.toString()], i = -1;
  listenerArray && (i = goog.events.ListenerMap.findListenerIndex_(listenerArray, listener, capture, opt_listenerScope));
  return -1 < i ? listenerArray[i] : null;
};
goog.events.ListenerMap.prototype.hasListener = function(opt_type, opt_capture) {
  var hasType = void 0 !== opt_type, typeStr = hasType ? opt_type.toString() : "", hasCapture = void 0 !== opt_capture;
  return module$contents$goog$object_some(this.listeners, function(listenerArray) {
    for (var i = 0; i < listenerArray.length; ++i) {
      if (!(hasType && listenerArray[i].type != typeStr || hasCapture && listenerArray[i].capture != opt_capture)) {
        return !0;
      }
    }
    return !1;
  });
};
goog.events.ListenerMap.findListenerIndex_ = function(listenerArray, listener, opt_useCapture, opt_listenerScope) {
  for (var i = 0; i < listenerArray.length; ++i) {
    var listenerObj = listenerArray[i];
    if (!listenerObj.removed && listenerObj.listener == listener && listenerObj.capture == !!opt_useCapture && listenerObj.handler == opt_listenerScope) {
      return i;
    }
  }
  return -1;
};
goog.events.Key = {};
goog.events.ListenableType = {};
goog.events.LISTENER_MAP_PROP_ = "closure_lm_" + (1E6 * Math.random() | 0);
goog.events.onString_ = "on";
goog.events.onStringMap_ = {};
goog.events.CaptureSimulationMode = {OFF_AND_FAIL:0, OFF_AND_SILENT:1, ON:2};
goog.events.CAPTURE_SIMULATION_MODE = 2;
goog.events.listenerCountEstimate_ = 0;
goog.events.listen = function(src, type, listener, opt_options, opt_handler) {
  if (opt_options && opt_options.once) {
    return goog.events.listenOnce(src, type, listener, opt_options, opt_handler);
  }
  if (Array.isArray(type)) {
    for (var i = 0; i < type.length; i++) {
      goog.events.listen(src, type[i], listener, opt_options, opt_handler);
    }
    return null;
  }
  listener = goog.events.wrapListener(listener);
  if (goog.events.Listenable.isImplementedBy(src)) {
    var capture = goog.isObject(opt_options) ? !!opt_options.capture : !!opt_options;
    return src.listen(type, listener, capture, opt_handler);
  }
  return goog.events.listen_(src, type, listener, !1, opt_options, opt_handler);
};
goog.events.listen_ = function(src, type, listener, callOnce, opt_options, opt_handler) {
  if (!type) {
    throw Error("Invalid event type");
  }
  var capture = goog.isObject(opt_options) ? !!opt_options.capture : !!opt_options, listenerMap = goog.events.getListenerMap_(src);
  listenerMap || (src[goog.events.LISTENER_MAP_PROP_] = listenerMap = new goog.events.ListenerMap(src));
  var listenerObj = listenerMap.add(type, listener, callOnce, capture, opt_handler);
  if (listenerObj.proxy) {
    return listenerObj;
  }
  var proxy = goog.events.getProxy();
  listenerObj.proxy = proxy;
  proxy.src = src;
  proxy.listener = listenerObj;
  if (src.addEventListener) {
    goog.events.BrowserFeature.PASSIVE_EVENTS || (opt_options = capture), void 0 === opt_options && (opt_options = !1), src.addEventListener(type.toString(), proxy, opt_options);
  } else if (src.attachEvent) {
    src.attachEvent(goog.events.getOnString_(type.toString()), proxy);
  } else if (src.addListener && src.removeListener) {
    goog.asserts.assert("change" === type, "MediaQueryList only has a change event"), src.addListener(proxy);
  } else {
    throw Error("addEventListener and attachEvent are unavailable.");
  }
  goog.events.listenerCountEstimate_++;
  return listenerObj;
};
goog.events.getProxy = function() {
  var proxyCallbackFunction = goog.events.handleBrowserEvent_, f = function(eventObject) {
    return proxyCallbackFunction.call(f.src, f.listener, eventObject);
  };
  return f;
};
goog.events.listenOnce = function(src, type, listener, opt_options, opt_handler) {
  if (Array.isArray(type)) {
    for (var i = 0; i < type.length; i++) {
      goog.events.listenOnce(src, type[i], listener, opt_options, opt_handler);
    }
    return null;
  }
  listener = goog.events.wrapListener(listener);
  if (goog.events.Listenable.isImplementedBy(src)) {
    var capture = goog.isObject(opt_options) ? !!opt_options.capture : !!opt_options;
    return src.listenOnce(type, listener, capture, opt_handler);
  }
  return goog.events.listen_(src, type, listener, !0, opt_options, opt_handler);
};
goog.events.listenWithWrapper = function(src, wrapper, listener, opt_capt, opt_handler) {
  wrapper.listen(src, listener, opt_capt, opt_handler);
};
goog.events.unlisten = function(src, type, listener, opt_options, opt_handler) {
  if (Array.isArray(type)) {
    for (var i = 0; i < type.length; i++) {
      goog.events.unlisten(src, type[i], listener, opt_options, opt_handler);
    }
    return null;
  }
  var capture = goog.isObject(opt_options) ? !!opt_options.capture : !!opt_options;
  listener = goog.events.wrapListener(listener);
  if (goog.events.Listenable.isImplementedBy(src)) {
    return src.unlisten(type, listener, capture, opt_handler);
  }
  if (!src) {
    return !1;
  }
  var listenerMap = goog.events.getListenerMap_(src);
  if (listenerMap) {
    var listenerObj = listenerMap.getListener(type, listener, capture, opt_handler);
    if (listenerObj) {
      return goog.events.unlistenByKey(listenerObj);
    }
  }
  return !1;
};
goog.events.unlistenByKey = function(key) {
  if ("number" === typeof key) {
    return !1;
  }
  var listener = key;
  if (!listener || listener.removed) {
    return !1;
  }
  var src = listener.src;
  if (goog.events.Listenable.isImplementedBy(src)) {
    return src.unlistenByKey(listener);
  }
  var type = listener.type, proxy = listener.proxy;
  src.removeEventListener ? src.removeEventListener(type, proxy, listener.capture) : src.detachEvent ? src.detachEvent(goog.events.getOnString_(type), proxy) : src.addListener && src.removeListener && src.removeListener(proxy);
  goog.events.listenerCountEstimate_--;
  var listenerMap = goog.events.getListenerMap_(src);
  listenerMap ? (listenerMap.removeByKey(listener), 0 == listenerMap.typeCount_ && (listenerMap.src = null, src[goog.events.LISTENER_MAP_PROP_] = null)) : listener.markAsRemoved();
  return !0;
};
goog.events.unlistenWithWrapper = function(src, wrapper, listener, opt_capt, opt_handler) {
  wrapper.unlisten(src, listener, opt_capt, opt_handler);
};
goog.events.removeAll = function(obj, opt_type) {
  if (!obj) {
    return 0;
  }
  if (goog.events.Listenable.isImplementedBy(obj)) {
    return obj.removeAllListeners(opt_type);
  }
  var listenerMap = goog.events.getListenerMap_(obj);
  if (!listenerMap) {
    return 0;
  }
  var count = 0, typeStr = opt_type && opt_type.toString(), type;
  for (type in listenerMap.listeners) {
    if (!typeStr || type == typeStr) {
      for (var listeners = listenerMap.listeners[type].concat(), i = 0; i < listeners.length; ++i) {
        goog.events.unlistenByKey(listeners[i]) && ++count;
      }
    }
  }
  return count;
};
goog.events.getListeners = function(obj, type, capture) {
  if (goog.events.Listenable.isImplementedBy(obj)) {
    return obj.getListeners(type, capture);
  }
  if (!obj) {
    return [];
  }
  var listenerMap = goog.events.getListenerMap_(obj);
  return listenerMap ? listenerMap.getListeners(type, capture) : [];
};
goog.events.getListener = function(src, type, listener, opt_capt, opt_handler) {
  listener = goog.events.wrapListener(listener);
  var capture = !!opt_capt;
  if (goog.events.Listenable.isImplementedBy(src)) {
    return src.getListener(type, listener, capture, opt_handler);
  }
  if (!src) {
    return null;
  }
  var listenerMap = goog.events.getListenerMap_(src);
  return listenerMap ? listenerMap.getListener(type, listener, capture, opt_handler) : null;
};
goog.events.hasListener = function(obj, opt_type, opt_capture) {
  if (goog.events.Listenable.isImplementedBy(obj)) {
    return obj.hasListener(opt_type, opt_capture);
  }
  var listenerMap = goog.events.getListenerMap_(obj);
  return !!listenerMap && listenerMap.hasListener(opt_type, opt_capture);
};
goog.events.expose = function(e) {
  var str = [], key;
  for (key in e) {
    e[key] && e[key].id ? str.push(key + " = " + e[key] + " (" + e[key].id + ")") : str.push(key + " = " + e[key]);
  }
  return str.join("\n");
};
goog.events.getOnString_ = function(type) {
  return type in goog.events.onStringMap_ ? goog.events.onStringMap_[type] : goog.events.onStringMap_[type] = goog.events.onString_ + type;
};
goog.events.fireListeners = function(obj, type, capture, eventObject) {
  return goog.events.Listenable.isImplementedBy(obj) ? obj.fireListeners(type, capture, eventObject) : goog.events.fireListeners_(obj, type, capture, eventObject);
};
goog.events.fireListeners_ = function(obj, type, capture, eventObject) {
  var retval = !0, listenerMap = goog.events.getListenerMap_(obj);
  if (listenerMap) {
    var listenerArray = listenerMap.listeners[type.toString()];
    if (listenerArray) {
      listenerArray = listenerArray.concat();
      for (var i = 0; i < listenerArray.length; i++) {
        var listener = listenerArray[i];
        if (listener && listener.capture == capture && !listener.removed) {
          var result = goog.events.fireListener(listener, eventObject);
          retval = retval && !1 !== result;
        }
      }
    }
  }
  return retval;
};
goog.events.fireListener = function(listener, eventObject) {
  var listenerFn = listener.listener, listenerHandler = listener.handler || listener.src;
  listener.callOnce && goog.events.unlistenByKey(listener);
  return listenerFn.call(listenerHandler, eventObject);
};
goog.events.getTotalListenerCount = function() {
  return goog.events.listenerCountEstimate_;
};
goog.events.dispatchEvent = function(src, e) {
  goog.asserts.assert(goog.events.Listenable.isImplementedBy(src), "Can not use goog.events.dispatchEvent with non-goog.events.Listenable instance.");
  return src.dispatchEvent(e);
};
goog.events.protectBrowserEventEntryPoint = function(errorHandler) {
  goog.events.handleBrowserEvent_ = errorHandler.protectEntryPoint(goog.events.handleBrowserEvent_);
};
goog.events.handleBrowserEvent_ = function(listener, opt_evt) {
  return listener.removed ? !0 : goog.events.fireListener(listener, new goog.events.BrowserEvent(opt_evt, this));
};
goog.events.markIeEvent_ = function(e) {
  var useReturnValue = !1;
  if (0 == e.keyCode) {
    try {
      e.keyCode = -1;
      return;
    } catch (ex) {
      useReturnValue = !0;
    }
  }
  if (useReturnValue || void 0 == e.returnValue) {
    e.returnValue = !0;
  }
};
goog.events.isMarkedIeEvent_ = function(e) {
  return 0 > e.keyCode || void 0 != e.returnValue;
};
goog.events.uniqueIdCounter_ = 0;
goog.events.getUniqueId = function(identifier) {
  return identifier + "_" + goog.events.uniqueIdCounter_++;
};
goog.events.getListenerMap_ = function(src) {
  var listenerMap = src[goog.events.LISTENER_MAP_PROP_];
  return listenerMap instanceof goog.events.ListenerMap ? listenerMap : null;
};
goog.events.LISTENER_WRAPPER_PROP_ = "__closure_events_fn_" + (1E9 * Math.random() >>> 0);
goog.events.wrapListener = function(listener) {
  goog.asserts.assert(listener, "Listener can not be null.");
  if ("function" === typeof listener) {
    return listener;
  }
  goog.asserts.assert(listener.handleEvent, "An object listener must have handleEvent method.");
  listener[goog.events.LISTENER_WRAPPER_PROP_] || (listener[goog.events.LISTENER_WRAPPER_PROP_] = function(e) {
    return listener.handleEvent(e);
  });
  return listener[goog.events.LISTENER_WRAPPER_PROP_];
};
goog.debug.entryPointRegistry.register(function(transformer) {
  goog.events.handleBrowserEvent_ = transformer(goog.events.handleBrowserEvent_);
});
goog.events.EventTarget = function() {
  goog.Disposable.call(this);
  this.eventTargetListeners_ = new goog.events.ListenerMap(this);
  this.actualEventTarget_ = this;
  this.parentEventTarget_ = null;
};
goog.inherits(goog.events.EventTarget, goog.Disposable);
goog.events.Listenable.addImplementation(goog.events.EventTarget);
goog.events.EventTarget.MAX_ANCESTORS_ = 1E3;
goog.events.EventTarget.prototype.getParentEventTarget = function() {
  return this.parentEventTarget_;
};
goog.events.EventTarget.prototype.addEventListener = function(type, handler, opt_capture, opt_handlerScope) {
  goog.events.listen(this, type, handler, opt_capture, opt_handlerScope);
};
goog.events.EventTarget.prototype.removeEventListener = function(type, handler, opt_capture, opt_handlerScope) {
  goog.events.unlisten(this, type, handler, opt_capture, opt_handlerScope);
};
goog.events.EventTarget.prototype.dispatchEvent = function(e) {
  this.assertInitialized_();
  var ancestor = this.getParentEventTarget();
  if (ancestor) {
    var ancestorsTree = [];
    for (var ancestorCount = 1; ancestor; ancestor = ancestor.getParentEventTarget()) {
      ancestorsTree.push(ancestor), goog.asserts.assert(++ancestorCount < goog.events.EventTarget.MAX_ANCESTORS_, "infinite loop");
    }
  }
  return goog.events.EventTarget.dispatchEventInternal_(this.actualEventTarget_, e, ancestorsTree);
};
goog.events.EventTarget.prototype.disposeInternal = function() {
  goog.events.EventTarget.superClass_.disposeInternal.call(this);
  this.removeAllListeners();
  this.parentEventTarget_ = null;
};
goog.events.EventTarget.prototype.listen = function(type, listener, opt_useCapture, opt_listenerScope) {
  this.assertInitialized_();
  return this.eventTargetListeners_.add(String(type), listener, !1, opt_useCapture, opt_listenerScope);
};
goog.events.EventTarget.prototype.listenOnce = function(type, listener, opt_useCapture, opt_listenerScope) {
  return this.eventTargetListeners_.add(String(type), listener, !0, opt_useCapture, opt_listenerScope);
};
goog.events.EventTarget.prototype.unlisten = function(type, listener, opt_useCapture, opt_listenerScope) {
  return this.eventTargetListeners_.remove(String(type), listener, opt_useCapture, opt_listenerScope);
};
goog.events.EventTarget.prototype.unlistenByKey = function(key) {
  return this.eventTargetListeners_.removeByKey(key);
};
goog.events.EventTarget.prototype.removeAllListeners = function(opt_type) {
  return this.eventTargetListeners_ ? this.eventTargetListeners_.removeAll(opt_type) : 0;
};
goog.events.EventTarget.prototype.fireListeners = function(type, capture, eventObject) {
  var listenerArray = this.eventTargetListeners_.listeners[String(type)];
  if (!listenerArray) {
    return !0;
  }
  listenerArray = listenerArray.concat();
  for (var rv = !0, i = 0; i < listenerArray.length; ++i) {
    var listener = listenerArray[i];
    if (listener && !listener.removed && listener.capture == capture) {
      var listenerFn = listener.listener, listenerHandler = listener.handler || listener.src;
      listener.callOnce && this.unlistenByKey(listener);
      rv = !1 !== listenerFn.call(listenerHandler, eventObject) && rv;
    }
  }
  return rv && !eventObject.defaultPrevented;
};
goog.events.EventTarget.prototype.getListeners = function(type, capture) {
  return this.eventTargetListeners_.getListeners(String(type), capture);
};
goog.events.EventTarget.prototype.getListener = function(type, listener, capture, opt_listenerScope) {
  return this.eventTargetListeners_.getListener(String(type), listener, capture, opt_listenerScope);
};
goog.events.EventTarget.prototype.hasListener = function(opt_type, opt_capture) {
  var id = void 0 !== opt_type ? String(opt_type) : void 0;
  return this.eventTargetListeners_.hasListener(id, opt_capture);
};
goog.events.EventTarget.prototype.assertInitialized_ = function() {
  goog.asserts.assert(this.eventTargetListeners_, "Event target is not initialized. Did you call the superclass (goog.events.EventTarget) constructor?");
};
goog.events.EventTarget.dispatchEventInternal_ = function(target, e, opt_ancestorsTree) {
  var type = e.type || e;
  if ("string" === typeof e) {
    e = new goog.events.Event(e, target);
  } else if (e instanceof goog.events.Event) {
    e.target = e.target || target;
  } else {
    var oldEvent = e;
    e = new goog.events.Event(type, target);
    module$contents$goog$object_extend(e, oldEvent);
  }
  var rv = !0;
  if (opt_ancestorsTree) {
    for (var i = opt_ancestorsTree.length - 1; !e.propagationStopped_ && 0 <= i; i--) {
      var currentTarget = e.currentTarget = opt_ancestorsTree[i];
      rv = currentTarget.fireListeners(type, !0, e) && rv;
    }
  }
  e.propagationStopped_ || (currentTarget = e.currentTarget = target, rv = currentTarget.fireListeners(type, !0, e) && rv, e.propagationStopped_ || (rv = currentTarget.fireListeners(type, !1, e) && rv));
  if (opt_ancestorsTree) {
    for (i = 0; !e.propagationStopped_ && i < opt_ancestorsTree.length; i++) {
      currentTarget = e.currentTarget = opt_ancestorsTree[i], rv = currentTarget.fireListeners(type, !1, e) && rv;
    }
  }
  return rv;
};
goog.json = {};
goog.json.Replacer = {};
goog.json.Reviver = {};
goog.json.USE_NATIVE_JSON = !1;
goog.json.isValid = function(s) {
  if (/^\s*$/.test(s)) {
    return !1;
  }
  var backslashesRe = /\\["\\\/bfnrtu]/g, simpleValuesRe = /(?:"[^"\\\n\r\u2028\u2029\x00-\x08\x0a-\x1f]*"|true|false|null|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)[\s\u2028\u2029]*(?=:|,|]|}|$)/g, openBracketsRe = /(?:^|:|,)(?:[\s\u2028\u2029]*\[)+/g, remainderRe = /^[\],:{}\s\u2028\u2029]*$/;
  return remainderRe.test(s.replace(backslashesRe, "@").replace(simpleValuesRe, "]").replace(openBracketsRe, ""));
};
goog.json.errorLogger_ = function() {
};
goog.json.setErrorLogger = function(errorLogger) {
  goog.json.errorLogger_ = errorLogger;
};
goog.json.parse = goog.json.USE_NATIVE_JSON ? goog.global.JSON.parse : function(s) {
  try {
    return goog.global.JSON.parse(s);
  } catch (ex) {
    var error = ex;
  }
  var o = String(s);
  if (goog.json.isValid(o)) {
    try {
      var result = eval("(" + o + ")");
      error && goog.json.errorLogger_("Invalid JSON: " + o, error);
      return result;
    } catch (ex$22) {
    }
  }
  throw Error("Invalid JSON string: " + o);
};
goog.json.serialize = goog.json.USE_NATIVE_JSON ? goog.global.JSON.stringify : function(object, opt_replacer) {
  return (new goog.json.Serializer(opt_replacer)).serialize(object);
};
goog.json.Serializer = function(opt_replacer) {
  this.replacer_ = opt_replacer;
};
goog.json.Serializer.prototype.serialize = function(object) {
  var sb = [];
  this.serializeInternal(object, sb);
  return sb.join("");
};
goog.json.Serializer.prototype.serializeInternal = function(object, sb) {
  if (null == object) {
    sb.push("null");
  } else {
    if ("object" == typeof object) {
      if (Array.isArray(object)) {
        this.serializeArray(object, sb);
        return;
      }
      if (object instanceof String || object instanceof Number || object instanceof Boolean) {
        object = object.valueOf();
      } else {
        this.serializeObject_(object, sb);
        return;
      }
    }
    switch(typeof object) {
      case "string":
        this.serializeString_(object, sb);
        break;
      case "number":
        this.serializeNumber_(object, sb);
        break;
      case "boolean":
        sb.push(String(object));
        break;
      case "function":
        sb.push("null");
        break;
      default:
        throw Error("Unknown type: " + typeof object);
    }
  }
};
goog.json.Serializer.charToJsonCharCache_ = {'"':'\\"', "\\":"\\\\", "/":"\\/", "\b":"\\b", "\f":"\\f", "\n":"\\n", "\r":"\\r", "\t":"\\t", "\v":"\\u000b"};
goog.json.Serializer.charsToReplace_ = /\uffff/.test("\uffff") ? /[\\"\x00-\x1f\x7f-\uffff]/g : /[\\"\x00-\x1f\x7f-\xff]/g;
goog.json.Serializer.prototype.serializeString_ = function(s, sb) {
  sb.push('"', s.replace(goog.json.Serializer.charsToReplace_, function(c) {
    var rv = goog.json.Serializer.charToJsonCharCache_[c];
    rv || (rv = "\\u" + (c.charCodeAt(0) | 65536).toString(16).slice(1), goog.json.Serializer.charToJsonCharCache_[c] = rv);
    return rv;
  }), '"');
};
goog.json.Serializer.prototype.serializeNumber_ = function(n, sb) {
  sb.push(isFinite(n) && !isNaN(n) ? String(n) : "null");
};
goog.json.Serializer.prototype.serializeArray = function(arr, sb) {
  var l = arr.length;
  sb.push("[");
  for (var sep = "", i = 0; i < l; i++) {
    sb.push(sep);
    var value = arr[i];
    this.serializeInternal(this.replacer_ ? this.replacer_.call(arr, String(i), value) : value, sb);
    sep = ",";
  }
  sb.push("]");
};
goog.json.Serializer.prototype.serializeObject_ = function(obj, sb) {
  sb.push("{");
  var sep = "", key;
  for (key in obj) {
    if (Object.prototype.hasOwnProperty.call(obj, key)) {
      var value = obj[key];
      "function" != typeof value && (sb.push(sep), this.serializeString_(key, sb), sb.push(":"), this.serializeInternal(this.replacer_ ? this.replacer_.call(obj, key, value) : value, sb), sep = ",");
    }
  }
  sb.push("}");
};
goog.json.hybrid = {};
goog.json.hybrid.stringify = goog.json.USE_NATIVE_JSON ? goog.global.JSON.stringify : function(obj) {
  if (goog.global.JSON) {
    try {
      return goog.global.JSON.stringify(obj);
    } catch (e) {
    }
  }
  return goog.json.serialize(obj);
};
goog.json.hybrid.parse_ = function(jsonString, fallbackParser) {
  if (goog.global.JSON) {
    try {
      var obj = goog.global.JSON.parse(jsonString);
      goog.asserts.assert("object" == typeof obj);
      return obj;
    } catch (e) {
    }
  }
  return fallbackParser(jsonString);
};
goog.json.hybrid.parse = goog.json.USE_NATIVE_JSON ? goog.global.JSON.parse : function(jsonString) {
  return goog.json.hybrid.parse_(jsonString, goog.json.parse);
};
goog.log = {};
goog.log.ENABLED = goog.debug.LOGGING_ENABLED;
goog.log.ROOT_LOGGER_NAME = "";
var third_party$javascript$closure$log$log$classdecl$var0 = function(name, value) {
  this.name = name;
  this.value = value;
};
third_party$javascript$closure$log$log$classdecl$var0.prototype.toString = function() {
  return this.name;
};
goog.log.Level = third_party$javascript$closure$log$log$classdecl$var0;
goog.log.Level.OFF = new goog.log.Level("OFF", Infinity);
goog.log.Level.SHOUT = new goog.log.Level("SHOUT", 1200);
goog.log.Level.SEVERE = new goog.log.Level("SEVERE", 1E3);
goog.log.Level.WARNING = new goog.log.Level("WARNING", 900);
goog.log.Level.INFO = new goog.log.Level("INFO", 800);
goog.log.Level.CONFIG = new goog.log.Level("CONFIG", 700);
goog.log.Level.FINE = new goog.log.Level("FINE", 500);
goog.log.Level.FINER = new goog.log.Level("FINER", 400);
goog.log.Level.FINEST = new goog.log.Level("FINEST", 300);
goog.log.Level.ALL = new goog.log.Level("ALL", 0);
goog.log.Level.PREDEFINED_LEVELS = [goog.log.Level.OFF, goog.log.Level.SHOUT, goog.log.Level.SEVERE, goog.log.Level.WARNING, goog.log.Level.INFO, goog.log.Level.CONFIG, goog.log.Level.FINE, goog.log.Level.FINER, goog.log.Level.FINEST, goog.log.Level.ALL];
goog.log.Level.predefinedLevelsCache_ = null;
goog.log.Level.createPredefinedLevelsCache_ = function() {
  goog.log.Level.predefinedLevelsCache_ = {};
  for (var i = 0, level; level = goog.log.Level.PREDEFINED_LEVELS[i]; i++) {
    goog.log.Level.predefinedLevelsCache_[level.value] = level, goog.log.Level.predefinedLevelsCache_[level.name] = level;
  }
};
goog.log.Level.getPredefinedLevel = function(name) {
  goog.log.Level.predefinedLevelsCache_ || goog.log.Level.createPredefinedLevelsCache_();
  return goog.log.Level.predefinedLevelsCache_[name] || null;
};
goog.log.Level.getPredefinedLevelByValue = function(value) {
  goog.log.Level.predefinedLevelsCache_ || goog.log.Level.createPredefinedLevelsCache_();
  if (value in goog.log.Level.predefinedLevelsCache_) {
    return goog.log.Level.predefinedLevelsCache_[value];
  }
  for (var i = 0; i < goog.log.Level.PREDEFINED_LEVELS.length; ++i) {
    var level = goog.log.Level.PREDEFINED_LEVELS[i];
    if (level.value <= value) {
      return level;
    }
  }
  return null;
};
var third_party$javascript$closure$log$log$classdecl$var1 = function() {
};
third_party$javascript$closure$log$log$classdecl$var1.prototype.getName = function() {
};
goog.log.Logger = third_party$javascript$closure$log$log$classdecl$var1;
goog.log.Logger.Level = goog.log.Level;
var third_party$javascript$closure$log$log$classdecl$var2 = function(capacity) {
  this.capacity_ = "number" === typeof capacity ? capacity : goog.log.LogBuffer.CAPACITY;
  this.clear();
};
third_party$javascript$closure$log$log$classdecl$var2.prototype.addRecord = function(level, msg, loggerName) {
  if (!this.isBufferingEnabled()) {
    return new goog.log.LogRecord(level, msg, loggerName);
  }
  var curIndex = (this.curIndex_ + 1) % this.capacity_;
  this.curIndex_ = curIndex;
  if (this.isFull_) {
    var ret = this.buffer_[curIndex];
    ret.reset(level, msg, loggerName);
    return ret;
  }
  this.isFull_ = curIndex == this.capacity_ - 1;
  return this.buffer_[curIndex] = new goog.log.LogRecord(level, msg, loggerName);
};
third_party$javascript$closure$log$log$classdecl$var2.prototype.isBufferingEnabled = function() {
  return 0 < this.capacity_;
};
third_party$javascript$closure$log$log$classdecl$var2.prototype.clear = function() {
  this.buffer_ = Array(this.capacity_);
  this.curIndex_ = -1;
  this.isFull_ = !1;
};
goog.log.LogBuffer = third_party$javascript$closure$log$log$classdecl$var2;
goog.log.LogBuffer.CAPACITY = 0;
goog.log.LogBuffer.getInstance = function() {
  goog.log.LogBuffer.instance_ || (goog.log.LogBuffer.instance_ = new goog.log.LogBuffer(goog.log.LogBuffer.CAPACITY));
  return goog.log.LogBuffer.instance_;
};
goog.log.LogBuffer.isBufferingEnabled = function() {
  return goog.log.LogBuffer.getInstance().isBufferingEnabled();
};
var third_party$javascript$closure$log$log$classdecl$var3 = function(level, msg, loggerName, time, sequenceNumber) {
  this.reset(level || goog.log.Level.OFF, msg, loggerName, time, sequenceNumber);
};
third_party$javascript$closure$log$log$classdecl$var3.prototype.reset = function(level) {
  this.level_ = level;
};
third_party$javascript$closure$log$log$classdecl$var3.prototype.getLevel = function() {
  return this.level_;
};
third_party$javascript$closure$log$log$classdecl$var3.prototype.setLevel = function(level) {
  this.level_ = level;
};
goog.log.LogRecord = third_party$javascript$closure$log$log$classdecl$var3;
goog.log.LogRecord.nextSequenceNumber_ = 0;
var third_party$javascript$closure$log$log$classdecl$var4 = function(name, parent) {
  parent = void 0 === parent ? null : parent;
  this.level = null;
  this.handlers = [];
  this.parent = parent || null;
  this.children = [];
  this.logger = {getName:function() {
    return name;
  }};
};
third_party$javascript$closure$log$log$classdecl$var4.prototype.getEffectiveLevel = function() {
  if (this.level) {
    return this.level;
  }
  if (this.parent) {
    return this.parent.getEffectiveLevel();
  }
  goog.asserts.fail("Root logger has no level set.");
  return goog.log.Level.OFF;
};
third_party$javascript$closure$log$log$classdecl$var4.prototype.publish = function(logRecord) {
  for (var target = this; target;) {
    target.handlers.forEach(function(handler) {
      handler(logRecord);
    }), target = target.parent;
  }
};
goog.log.LogRegistryEntry_ = third_party$javascript$closure$log$log$classdecl$var4;
var third_party$javascript$closure$log$log$classdecl$var5 = function() {
  this.entries = {};
  var rootLogRegistryEntry = new goog.log.LogRegistryEntry_(goog.log.ROOT_LOGGER_NAME);
  rootLogRegistryEntry.level = goog.log.Level.CONFIG;
  this.entries[goog.log.ROOT_LOGGER_NAME] = rootLogRegistryEntry;
};
third_party$javascript$closure$log$log$classdecl$var5.prototype.getLogRegistryEntry = function(name, level) {
  var entry = this.entries[name];
  if (entry) {
    return void 0 !== level && (entry.level = level), entry;
  }
  var lastDotIndex = name.lastIndexOf("."), parentName = name.slice(0, Math.max(lastDotIndex, 0)), parentLogRegistryEntry = this.getLogRegistryEntry(parentName), logRegistryEntry = new goog.log.LogRegistryEntry_(name, parentLogRegistryEntry);
  this.entries[name] = logRegistryEntry;
  parentLogRegistryEntry.children.push(logRegistryEntry);
  void 0 !== level && (logRegistryEntry.level = level);
  return logRegistryEntry;
};
third_party$javascript$closure$log$log$classdecl$var5.prototype.getAllLoggers = function() {
  var $jscomp$this = this;
  return Object.keys(this.entries).map(function(loggerName) {
    return $jscomp$this.entries[loggerName].logger;
  });
};
goog.log.LogRegistry_ = third_party$javascript$closure$log$log$classdecl$var5;
goog.log.LogRegistry_.getInstance = function() {
  goog.log.LogRegistry_.instance_ || (goog.log.LogRegistry_.instance_ = new goog.log.LogRegistry_());
  return goog.log.LogRegistry_.instance_;
};
goog.log.getLogger = function(name, level) {
  if (goog.log.ENABLED) {
    var loggerEntry = goog.log.LogRegistry_.getInstance().getLogRegistryEntry(name, level);
    return loggerEntry.logger;
  }
  return null;
};
goog.log.getRootLogger = function() {
  if (goog.log.ENABLED) {
    var loggerEntry = goog.log.LogRegistry_.getInstance().getLogRegistryEntry(goog.log.ROOT_LOGGER_NAME);
    return loggerEntry.logger;
  }
  return null;
};
goog.log.addHandler = function(logger, handler) {
  if (goog.log.ENABLED && logger) {
    var loggerEntry = goog.log.LogRegistry_.getInstance().getLogRegistryEntry(logger.getName());
    loggerEntry.handlers.push(handler);
  }
};
goog.log.removeHandler = function(logger, handler) {
  if (goog.log.ENABLED && logger) {
    var loggerEntry = goog.log.LogRegistry_.getInstance().getLogRegistryEntry(logger.getName()), indexOfHandler = loggerEntry.handlers.indexOf(handler);
    if (-1 !== indexOfHandler) {
      return loggerEntry.handlers.splice(indexOfHandler, 1), !0;
    }
  }
  return !1;
};
goog.log.setLevel = function(logger, level) {
  if (goog.log.ENABLED && logger) {
    var loggerEntry = goog.log.LogRegistry_.getInstance().getLogRegistryEntry(logger.getName());
    loggerEntry.level = level;
  }
};
goog.log.getLevel = function(logger) {
  if (goog.log.ENABLED && logger) {
    var loggerEntry = goog.log.LogRegistry_.getInstance().getLogRegistryEntry(logger.getName());
    return loggerEntry.level;
  }
  return null;
};
goog.log.getEffectiveLevel = function(logger) {
  if (goog.log.ENABLED && logger) {
    var loggerEntry = goog.log.LogRegistry_.getInstance().getLogRegistryEntry(logger.getName());
    return loggerEntry.getEffectiveLevel();
  }
  return goog.log.Level.OFF;
};
goog.log.isLoggable = function(logger, level) {
  return goog.log.ENABLED && logger && level ? level.value >= goog.log.getEffectiveLevel(logger).value : !1;
};
goog.log.getAllLoggers = function() {
  return goog.log.ENABLED ? goog.log.LogRegistry_.getInstance().getAllLoggers() : [];
};
goog.log.getLogRecord = function(logger, level, msg) {
  var logRecord = goog.log.LogBuffer.getInstance().addRecord(level || goog.log.Level.OFF, msg, logger.getName());
  return logRecord;
};
goog.log.publishLogRecord = function(logger, logRecord) {
  if (goog.log.ENABLED && logger && goog.log.isLoggable(logger, logRecord.getLevel())) {
    var loggerEntry = goog.log.LogRegistry_.getInstance().getLogRegistryEntry(logger.getName());
    loggerEntry.publish(logRecord);
  }
};
goog.log.log = function(logger, level, msg) {
  if (goog.log.ENABLED && logger && goog.log.isLoggable(logger, level)) {
    level = level || goog.log.Level.OFF;
    var loggerEntry = goog.log.LogRegistry_.getInstance().getLogRegistryEntry(logger.getName());
    "function" === typeof msg && (msg = msg());
    var logRecord = goog.log.LogBuffer.getInstance().addRecord(level, msg, logger.getName());
    loggerEntry.publish(logRecord);
  }
};
goog.log.error = function(logger, msg, exception) {
  goog.log.ENABLED && logger && goog.log.log(logger, goog.log.Level.SEVERE, msg, exception);
};
goog.log.warning = function(logger, msg, exception) {
  goog.log.ENABLED && logger && goog.log.log(logger, goog.log.Level.WARNING, msg, exception);
};
goog.log.info = function(logger, msg, exception) {
  goog.log.ENABLED && logger && goog.log.log(logger, goog.log.Level.INFO, msg, exception);
};
goog.log.fine = function(logger, msg, exception) {
  goog.log.ENABLED && logger && goog.log.log(logger, goog.log.Level.FINE, msg, exception);
};
goog.net = {};
goog.net.ErrorCode = {NO_ERROR:0, ACCESS_DENIED:1, FILE_NOT_FOUND:2, FF_SILENT_ERROR:3, CUSTOM_ERROR:4, EXCEPTION:5, HTTP_ERROR:6, ABORT:7, TIMEOUT:8, OFFLINE:9,};
goog.net.ErrorCode.getDebugMessage = function(errorCode) {
  switch(errorCode) {
    case goog.net.ErrorCode.NO_ERROR:
      return "No Error";
    case goog.net.ErrorCode.ACCESS_DENIED:
      return "Access denied to content document";
    case goog.net.ErrorCode.FILE_NOT_FOUND:
      return "File not found";
    case goog.net.ErrorCode.FF_SILENT_ERROR:
      return "Firefox silently errored";
    case goog.net.ErrorCode.CUSTOM_ERROR:
      return "Application custom error";
    case goog.net.ErrorCode.EXCEPTION:
      return "An exception occurred";
    case goog.net.ErrorCode.HTTP_ERROR:
      return "Http response at 400 or 500 level";
    case goog.net.ErrorCode.ABORT:
      return "Request was aborted";
    case goog.net.ErrorCode.TIMEOUT:
      return "Request timed out";
    case goog.net.ErrorCode.OFFLINE:
      return "The resource is not available offline";
    default:
      return "Unrecognized error code";
  }
};
goog.net.EventType = {COMPLETE:"complete", SUCCESS:"success", ERROR:"error", ABORT:"abort", READY:"ready", READY_STATE_CHANGE:"readystatechange", TIMEOUT:"timeout", INCREMENTAL_DATA:"incrementaldata", PROGRESS:"progress", DOWNLOAD_PROGRESS:"downloadprogress", UPLOAD_PROGRESS:"uploadprogress",};
goog.net.HttpStatus = {CONTINUE:100, SWITCHING_PROTOCOLS:101, OK:200, CREATED:201, ACCEPTED:202, NON_AUTHORITATIVE_INFORMATION:203, NO_CONTENT:204, RESET_CONTENT:205, PARTIAL_CONTENT:206, MULTI_STATUS:207, MULTIPLE_CHOICES:300, MOVED_PERMANENTLY:301, FOUND:302, SEE_OTHER:303, NOT_MODIFIED:304, USE_PROXY:305, TEMPORARY_REDIRECT:307, PERMANENT_REDIRECT:308, BAD_REQUEST:400, UNAUTHORIZED:401, PAYMENT_REQUIRED:402, FORBIDDEN:403, NOT_FOUND:404, METHOD_NOT_ALLOWED:405, NOT_ACCEPTABLE:406, PROXY_AUTHENTICATION_REQUIRED:407, 
REQUEST_TIMEOUT:408, CONFLICT:409, GONE:410, LENGTH_REQUIRED:411, PRECONDITION_FAILED:412, REQUEST_ENTITY_TOO_LARGE:413, REQUEST_URI_TOO_LONG:414, UNSUPPORTED_MEDIA_TYPE:415, REQUEST_RANGE_NOT_SATISFIABLE:416, EXPECTATION_FAILED:417, UNPROCESSABLE_ENTITY:422, LOCKED:423, FAILED_DEPENDENCY:424, PRECONDITION_REQUIRED:428, TOO_MANY_REQUESTS:429, REQUEST_HEADER_FIELDS_TOO_LARGE:431, CLIENT_CLOSED_REQUEST:499, INTERNAL_SERVER_ERROR:500, NOT_IMPLEMENTED:501, BAD_GATEWAY:502, SERVICE_UNAVAILABLE:503, GATEWAY_TIMEOUT:504, 
HTTP_VERSION_NOT_SUPPORTED:505, INSUFFICIENT_STORAGE:507, NETWORK_AUTHENTICATION_REQUIRED:511, QUIRK_IE_NO_CONTENT:1223,};
goog.net.HttpStatus.isSuccess = function(status) {
  switch(status) {
    case goog.net.HttpStatus.OK:
    case goog.net.HttpStatus.CREATED:
    case goog.net.HttpStatus.ACCEPTED:
    case goog.net.HttpStatus.NO_CONTENT:
    case goog.net.HttpStatus.PARTIAL_CONTENT:
    case goog.net.HttpStatus.NOT_MODIFIED:
    case goog.net.HttpStatus.QUIRK_IE_NO_CONTENT:
      return !0;
    default:
      return !1;
  }
};
goog.net.XhrLike = function() {
};
goog.net.XhrLike.prototype.open = function() {
};
goog.net.XhrLike.prototype.send = function() {
};
goog.net.XhrLike.prototype.abort = function() {
};
goog.net.XhrLike.prototype.setRequestHeader = function() {
};
goog.net.XhrLike.prototype.getResponseHeader = function() {
};
goog.net.XhrLike.prototype.getAllResponseHeaders = function() {
};
goog.net.XhrLike.prototype.setTrustToken = function() {
};
goog.net.XmlHttpFactory = function() {
};
goog.net.XmlHttpFactory.prototype.cachedOptions_ = null;
goog.net.XmlHttpFactory.prototype.getOptions = function() {
  return this.cachedOptions_ || (this.cachedOptions_ = this.internalGetOptions());
};
goog.net.WrapperXmlHttpFactory = function(xhrFactory, optionsFactory) {
  this.xhrFactory_ = xhrFactory;
  this.optionsFactory_ = optionsFactory;
};
goog.inherits(goog.net.WrapperXmlHttpFactory, goog.net.XmlHttpFactory);
goog.net.WrapperXmlHttpFactory.prototype.createInstance = function() {
  return this.xhrFactory_();
};
goog.net.WrapperXmlHttpFactory.prototype.getOptions = function() {
  return this.optionsFactory_();
};
goog.net.XmlHttp = function() {
  return goog.net.XmlHttp.factory_.createInstance();
};
goog.net.XmlHttp.ASSUME_NATIVE_XHR = !1;
goog.net.XmlHttpDefines = {};
goog.net.XmlHttpDefines.ASSUME_NATIVE_XHR = !1;
goog.net.XmlHttp.getOptions = function() {
  return goog.net.XmlHttp.factory_.getOptions();
};
goog.net.XmlHttp.OptionType = {USE_NULL_FUNCTION:0, LOCAL_REQUEST_ERROR:1,};
goog.net.XmlHttp.ReadyState = {UNINITIALIZED:0, LOADING:1, LOADED:2, INTERACTIVE:3, COMPLETE:4,};
goog.net.XmlHttp.setFactory = function(factory, optionsFactory) {
  goog.net.XmlHttp.setGlobalFactory(new goog.net.WrapperXmlHttpFactory(goog.asserts.assert(factory), goog.asserts.assert(optionsFactory)));
};
goog.net.XmlHttp.setGlobalFactory = function(factory) {
  goog.net.XmlHttp.factory_ = factory;
};
goog.net.DefaultXmlHttpFactory = function() {
};
goog.inherits(goog.net.DefaultXmlHttpFactory, goog.net.XmlHttpFactory);
goog.net.DefaultXmlHttpFactory.prototype.createInstance = function() {
  var progId = this.getProgId_();
  return progId ? new ActiveXObject(progId) : new XMLHttpRequest();
};
goog.net.DefaultXmlHttpFactory.prototype.internalGetOptions = function() {
  var progId = this.getProgId_(), options = {};
  progId && (options[goog.net.XmlHttp.OptionType.USE_NULL_FUNCTION] = !0, options[goog.net.XmlHttp.OptionType.LOCAL_REQUEST_ERROR] = !0);
  return options;
};
goog.net.DefaultXmlHttpFactory.prototype.getProgId_ = function() {
  if (goog.net.XmlHttp.ASSUME_NATIVE_XHR || goog.net.XmlHttpDefines.ASSUME_NATIVE_XHR) {
    return "";
  }
  if (!this.ieProgId_ && "undefined" == typeof XMLHttpRequest && "undefined" != typeof ActiveXObject) {
    for (var ACTIVE_X_IDENTS = ["MSXML2.XMLHTTP.6.0", "MSXML2.XMLHTTP.3.0", "MSXML2.XMLHTTP", "Microsoft.XMLHTTP",], i = 0; i < ACTIVE_X_IDENTS.length; i++) {
      var candidate = ACTIVE_X_IDENTS[i];
      try {
        return new ActiveXObject(candidate), this.ieProgId_ = candidate;
      } catch (e) {
      }
    }
    throw Error("Could not create ActiveXObject. ActiveX might be disabled, or MSXML might not be installed");
  }
  return this.ieProgId_;
};
goog.net.XmlHttp.setGlobalFactory(new goog.net.DefaultXmlHttpFactory());
goog.promise = {};
var module$contents$goog$promise$Resolver_Resolver = function() {
};
goog.promise.Resolver = module$contents$goog$promise$Resolver_Resolver;
function module$contents$goog$Thenable_Thenable() {
}
module$contents$goog$Thenable_Thenable.prototype.then = function() {
};
module$contents$goog$Thenable_Thenable.IMPLEMENTED_BY_PROP = "$goog_Thenable";
module$contents$goog$Thenable_Thenable.addImplementation = function(ctor) {
  ctor.prototype[module$contents$goog$Thenable_Thenable.IMPLEMENTED_BY_PROP] = !0;
};
module$contents$goog$Thenable_Thenable.isImplementedBy = function(object) {
  if (!object) {
    return !1;
  }
  try {
    return !!object[module$contents$goog$Thenable_Thenable.IMPLEMENTED_BY_PROP];
  } catch (e) {
    return !1;
  }
};
goog.Thenable = module$contents$goog$Thenable_Thenable;
goog.Promise = function(resolver, opt_context) {
  this.state_ = goog.Promise.State_.PENDING;
  this.result_ = void 0;
  this.callbackEntriesTail_ = this.callbackEntries_ = this.parent_ = null;
  this.executing_ = !1;
  0 < goog.Promise.UNHANDLED_REJECTION_DELAY ? this.unhandledRejectionId_ = 0 : 0 == goog.Promise.UNHANDLED_REJECTION_DELAY && (this.hadUnhandledRejection_ = !1);
  goog.Promise.LONG_STACK_TRACES && (this.stack_ = [], this.addStackTrace_(Error("created")), this.currentStep_ = 0);
  if (resolver != goog.functions.UNDEFINED) {
    try {
      var self = this;
      resolver.call(opt_context, function(value) {
        self.resolve_(goog.Promise.State_.FULFILLED, value);
      }, function(reason) {
        if (goog.DEBUG && !(reason instanceof goog.Promise.CancellationError)) {
          try {
            if (reason instanceof Error) {
              throw reason;
            }
            throw Error("Promise rejected.");
          } catch (e) {
          }
        }
        self.resolve_(goog.Promise.State_.REJECTED, reason);
      });
    } catch (e) {
      this.resolve_(goog.Promise.State_.REJECTED, e);
    }
  }
};
goog.Promise.LONG_STACK_TRACES = !1;
goog.Promise.UNHANDLED_REJECTION_DELAY = 0;
goog.Promise.State_ = {PENDING:0, BLOCKED:1, FULFILLED:2, REJECTED:3};
goog.Promise.CallbackEntry_ = function() {
  this.next = this.context = this.onRejected = this.onFulfilled = this.child = null;
  this.always = !1;
};
goog.Promise.CallbackEntry_.prototype.reset = function() {
  this.context = this.onRejected = this.onFulfilled = this.child = null;
  this.always = !1;
};
goog.Promise.DEFAULT_MAX_UNUSED = 100;
goog.Promise.freelist_ = new module$contents$goog$async$FreeList_FreeList(function() {
  return new goog.Promise.CallbackEntry_();
}, function(item) {
  item.reset();
}, goog.Promise.DEFAULT_MAX_UNUSED);
goog.Promise.getCallbackEntry_ = function(onFulfilled, onRejected, context) {
  var entry = goog.Promise.freelist_.get();
  entry.onFulfilled = onFulfilled;
  entry.onRejected = onRejected;
  entry.context = context;
  return entry;
};
goog.Promise.returnEntry_ = function(entry) {
  goog.Promise.freelist_.put(entry);
};
goog.Promise.resolve = function(opt_value) {
  if (opt_value instanceof goog.Promise) {
    return opt_value;
  }
  var promise = new goog.Promise(goog.functions.UNDEFINED);
  promise.resolve_(goog.Promise.State_.FULFILLED, opt_value);
  return promise;
};
goog.Promise.reject = function(opt_reason) {
  return new goog.Promise(function(resolve, reject) {
    reject(opt_reason);
  });
};
goog.Promise.resolveThen_ = function(value, onFulfilled, onRejected) {
  var isThenable = goog.Promise.maybeThen_(value, onFulfilled, onRejected, null);
  isThenable || module$contents$goog$async$run_run(goog.partial(onFulfilled, value));
};
goog.Promise.race = function(promises) {
  return new goog.Promise(function(resolve, reject) {
    promises.length || resolve(void 0);
    for (var i = 0, promise; i < promises.length; i++) {
      promise = promises[i], goog.Promise.resolveThen_(promise, resolve, reject);
    }
  });
};
goog.Promise.all = function(promises) {
  return new goog.Promise(function(resolve, reject) {
    var toFulfill = promises.length, values = [];
    if (toFulfill) {
      for (var onFulfill = function(index, value) {
        toFulfill--;
        values[index] = value;
        0 == toFulfill && resolve(values);
      }, onReject = function(reason) {
        reject(reason);
      }, i = 0, promise; i < promises.length; i++) {
        promise = promises[i], goog.Promise.resolveThen_(promise, goog.partial(onFulfill, i), onReject);
      }
    } else {
      resolve(values);
    }
  });
};
goog.Promise.allSettled = function(promises) {
  return new goog.Promise(function(resolve) {
    var toSettle = promises.length, results = [];
    if (toSettle) {
      for (var onSettled = function(index, fulfilled, result) {
        toSettle--;
        results[index] = fulfilled ? {fulfilled:!0, value:result} : {fulfilled:!1, reason:result};
        0 == toSettle && resolve(results);
      }, i = 0, promise; i < promises.length; i++) {
        promise = promises[i], goog.Promise.resolveThen_(promise, goog.partial(onSettled, i, !0), goog.partial(onSettled, i, !1));
      }
    } else {
      resolve(results);
    }
  });
};
goog.Promise.firstFulfilled = function(promises) {
  return new goog.Promise(function(resolve, reject) {
    var toReject = promises.length, reasons = [];
    if (toReject) {
      for (var onFulfill = function(value) {
        resolve(value);
      }, onReject = function(index, reason) {
        toReject--;
        reasons[index] = reason;
        0 == toReject && reject(reasons);
      }, i = 0, promise; i < promises.length; i++) {
        promise = promises[i], goog.Promise.resolveThen_(promise, onFulfill, goog.partial(onReject, i));
      }
    } else {
      resolve(void 0);
    }
  });
};
goog.Promise.withResolver = function() {
  var resolve, reject, promise = new goog.Promise(function(rs, rj) {
    resolve = rs;
    reject = rj;
  });
  return new goog.Promise.Resolver_(promise, resolve, reject);
};
goog.Promise.prototype.then = function(opt_onFulfilled, opt_onRejected, opt_context) {
  null != opt_onFulfilled && goog.asserts.assertFunction(opt_onFulfilled, "opt_onFulfilled should be a function.");
  null != opt_onRejected && goog.asserts.assertFunction(opt_onRejected, "opt_onRejected should be a function. Did you pass opt_context as the second argument instead of the third?");
  goog.Promise.LONG_STACK_TRACES && this.addStackTrace_(Error("then"));
  return this.addChildPromise_("function" === typeof opt_onFulfilled ? opt_onFulfilled : null, "function" === typeof opt_onRejected ? opt_onRejected : null, opt_context);
};
module$contents$goog$Thenable_Thenable.addImplementation(goog.Promise);
goog.Promise.prototype.thenVoid = function(opt_onFulfilled, opt_onRejected, opt_context) {
  null != opt_onFulfilled && goog.asserts.assertFunction(opt_onFulfilled, "opt_onFulfilled should be a function.");
  null != opt_onRejected && goog.asserts.assertFunction(opt_onRejected, "opt_onRejected should be a function. Did you pass opt_context as the second argument instead of the third?");
  goog.Promise.LONG_STACK_TRACES && this.addStackTrace_(Error("then"));
  this.addCallbackEntry_(goog.Promise.getCallbackEntry_(opt_onFulfilled || goog.functions.UNDEFINED, opt_onRejected || null, opt_context));
};
goog.Promise.prototype.thenCatch = function(onRejected, opt_context) {
  goog.Promise.LONG_STACK_TRACES && this.addStackTrace_(Error("thenCatch"));
  return this.addChildPromise_(null, onRejected, opt_context);
};
goog.Promise.prototype.catch = goog.Promise.prototype.thenCatch;
goog.Promise.prototype.cancel = function(opt_message) {
  if (this.state_ == goog.Promise.State_.PENDING) {
    var err = new goog.Promise.CancellationError(opt_message);
    module$contents$goog$async$run_run(function() {
      this.cancelInternal_(err);
    }, this);
  }
};
goog.Promise.prototype.cancelInternal_ = function(err) {
  this.state_ == goog.Promise.State_.PENDING && (this.parent_ ? (this.parent_.cancelChild_(this, err), this.parent_ = null) : this.resolve_(goog.Promise.State_.REJECTED, err));
};
goog.Promise.prototype.cancelChild_ = function(childPromise, err) {
  if (this.callbackEntries_) {
    for (var childCount = 0, childEntry = null, beforeChildEntry = null, entry = this.callbackEntries_; entry && (entry.always || (childCount++, entry.child == childPromise && (childEntry = entry), !(childEntry && 1 < childCount))); entry = entry.next) {
      childEntry || (beforeChildEntry = entry);
    }
    childEntry && (this.state_ == goog.Promise.State_.PENDING && 1 == childCount ? this.cancelInternal_(err) : (beforeChildEntry ? this.removeEntryAfter_(beforeChildEntry) : this.popEntry_(), this.executeCallback_(childEntry, goog.Promise.State_.REJECTED, err)));
  }
};
goog.Promise.prototype.addCallbackEntry_ = function(callbackEntry) {
  this.hasEntry_() || this.state_ != goog.Promise.State_.FULFILLED && this.state_ != goog.Promise.State_.REJECTED || this.scheduleCallbacks_();
  this.queueEntry_(callbackEntry);
};
goog.Promise.prototype.addChildPromise_ = function(onFulfilled, onRejected, opt_context) {
  var callbackEntry = goog.Promise.getCallbackEntry_(null, null, null);
  callbackEntry.child = new goog.Promise(function(resolve, reject) {
    callbackEntry.onFulfilled = onFulfilled ? function(value) {
      try {
        var result = onFulfilled.call(opt_context, value);
        resolve(result);
      } catch (err$23) {
        reject(err$23);
      }
    } : resolve;
    callbackEntry.onRejected = onRejected ? function(reason) {
      try {
        var result = onRejected.call(opt_context, reason);
        void 0 === result && reason instanceof goog.Promise.CancellationError ? reject(reason) : resolve(result);
      } catch (err$24) {
        reject(err$24);
      }
    } : reject;
  });
  callbackEntry.child.parent_ = this;
  this.addCallbackEntry_(callbackEntry);
  return callbackEntry.child;
};
goog.Promise.prototype.unblockAndFulfill_ = function(value) {
  goog.asserts.assert(this.state_ == goog.Promise.State_.BLOCKED);
  this.state_ = goog.Promise.State_.PENDING;
  this.resolve_(goog.Promise.State_.FULFILLED, value);
};
goog.Promise.prototype.unblockAndReject_ = function(reason) {
  goog.asserts.assert(this.state_ == goog.Promise.State_.BLOCKED);
  this.state_ = goog.Promise.State_.PENDING;
  this.resolve_(goog.Promise.State_.REJECTED, reason);
};
goog.Promise.prototype.resolve_ = function(state, x) {
  if (this.state_ == goog.Promise.State_.PENDING) {
    this === x && (state = goog.Promise.State_.REJECTED, x = new TypeError("Promise cannot resolve to itself"));
    this.state_ = goog.Promise.State_.BLOCKED;
    var isThenable = goog.Promise.maybeThen_(x, this.unblockAndFulfill_, this.unblockAndReject_, this);
    isThenable || (this.result_ = x, this.state_ = state, this.parent_ = null, this.scheduleCallbacks_(), state != goog.Promise.State_.REJECTED || x instanceof goog.Promise.CancellationError || goog.Promise.addUnhandledRejection_(this, x));
  }
};
goog.Promise.maybeThen_ = function(value, onFulfilled, onRejected, context) {
  if (value instanceof goog.Promise) {
    return value.thenVoid(onFulfilled, onRejected, context), !0;
  }
  if (module$contents$goog$Thenable_Thenable.isImplementedBy(value)) {
    return value.then(onFulfilled, onRejected, context), !0;
  }
  if (goog.isObject(value)) {
    var thenable = value;
    try {
      var then = thenable.then;
      if ("function" === typeof then) {
        return goog.Promise.tryThen_(thenable, then, onFulfilled, onRejected, context), !0;
      }
    } catch (e) {
      return onRejected.call(context, e), !0;
    }
  }
  return !1;
};
goog.Promise.tryThen_ = function(thenable, then, onFulfilled, onRejected, context) {
  var called = !1, resolve = function(value) {
    called || (called = !0, onFulfilled.call(context, value));
  }, reject = function(reason) {
    called || (called = !0, onRejected.call(context, reason));
  };
  try {
    then.call(thenable, resolve, reject);
  } catch (e) {
    reject(e);
  }
};
goog.Promise.prototype.scheduleCallbacks_ = function() {
  this.executing_ || (this.executing_ = !0, module$contents$goog$async$run_run(this.executeCallbacks_, this));
};
goog.Promise.prototype.hasEntry_ = function() {
  return !!this.callbackEntries_;
};
goog.Promise.prototype.queueEntry_ = function(entry) {
  goog.asserts.assert(null != entry.onFulfilled);
  this.callbackEntriesTail_ ? this.callbackEntriesTail_.next = entry : this.callbackEntries_ = entry;
  this.callbackEntriesTail_ = entry;
};
goog.Promise.prototype.popEntry_ = function() {
  var entry = null;
  this.callbackEntries_ && (entry = this.callbackEntries_, this.callbackEntries_ = entry.next, entry.next = null);
  this.callbackEntries_ || (this.callbackEntriesTail_ = null);
  null != entry && goog.asserts.assert(null != entry.onFulfilled);
  return entry;
};
goog.Promise.prototype.removeEntryAfter_ = function(previous) {
  goog.asserts.assert(this.callbackEntries_);
  goog.asserts.assert(null != previous);
  previous.next == this.callbackEntriesTail_ && (this.callbackEntriesTail_ = previous);
  previous.next = previous.next.next;
};
goog.Promise.prototype.executeCallbacks_ = function() {
  for (var entry; entry = this.popEntry_();) {
    goog.Promise.LONG_STACK_TRACES && this.currentStep_++, this.executeCallback_(entry, this.state_, this.result_);
  }
  this.executing_ = !1;
};
goog.Promise.prototype.executeCallback_ = function(callbackEntry, state, result) {
  state == goog.Promise.State_.REJECTED && callbackEntry.onRejected && !callbackEntry.always && this.removeUnhandledRejection_();
  if (callbackEntry.child) {
    callbackEntry.child.parent_ = null, goog.Promise.invokeCallback_(callbackEntry, state, result);
  } else {
    try {
      callbackEntry.always ? callbackEntry.onFulfilled.call(callbackEntry.context) : goog.Promise.invokeCallback_(callbackEntry, state, result);
    } catch (err$25) {
      goog.Promise.handleRejection_.call(null, err$25);
    }
  }
  goog.Promise.returnEntry_(callbackEntry);
};
goog.Promise.invokeCallback_ = function(callbackEntry, state, result) {
  state == goog.Promise.State_.FULFILLED ? callbackEntry.onFulfilled.call(callbackEntry.context, result) : callbackEntry.onRejected && callbackEntry.onRejected.call(callbackEntry.context, result);
};
goog.Promise.prototype.addStackTrace_ = function(err) {
  if (goog.Promise.LONG_STACK_TRACES && "string" === typeof err.stack) {
    var trace = err.stack.split("\n", 4)[3], message = err.message;
    message += Array(11 - message.length).join(" ");
    this.stack_.push(message + trace);
  }
};
goog.Promise.prototype.appendLongStack_ = function(err) {
  if (goog.Promise.LONG_STACK_TRACES && err && "string" === typeof err.stack && this.stack_.length) {
    for (var longTrace = ["Promise trace:"], promise = this; promise; promise = promise.parent_) {
      for (var i = this.currentStep_; 0 <= i; i--) {
        longTrace.push(promise.stack_[i]);
      }
      longTrace.push("Value: [" + (promise.state_ == goog.Promise.State_.REJECTED ? "REJECTED" : "FULFILLED") + "] <" + String(promise.result_) + ">");
    }
    err.stack += "\n\n" + longTrace.join("\n");
  }
};
goog.Promise.prototype.removeUnhandledRejection_ = function() {
  if (0 < goog.Promise.UNHANDLED_REJECTION_DELAY) {
    for (var p = this; p && p.unhandledRejectionId_; p = p.parent_) {
      goog.global.clearTimeout(p.unhandledRejectionId_), p.unhandledRejectionId_ = 0;
    }
  } else if (0 == goog.Promise.UNHANDLED_REJECTION_DELAY) {
    for (p = this; p && p.hadUnhandledRejection_; p = p.parent_) {
      p.hadUnhandledRejection_ = !1;
    }
  }
};
goog.Promise.addUnhandledRejection_ = function(promise, reason) {
  0 < goog.Promise.UNHANDLED_REJECTION_DELAY ? promise.unhandledRejectionId_ = goog.global.setTimeout(function() {
    promise.appendLongStack_(reason);
    goog.Promise.handleRejection_.call(null, reason);
  }, goog.Promise.UNHANDLED_REJECTION_DELAY) : 0 == goog.Promise.UNHANDLED_REJECTION_DELAY && (promise.hadUnhandledRejection_ = !0, module$contents$goog$async$run_run(function() {
    promise.hadUnhandledRejection_ && (promise.appendLongStack_(reason), goog.Promise.handleRejection_.call(null, reason));
  }));
};
goog.Promise.handleRejection_ = module$contents$goog$async$throwException_throwException;
goog.Promise.setUnhandledRejectionHandler = function(handler) {
  goog.Promise.handleRejection_ = handler;
};
goog.Promise.CancellationError = function(opt_message) {
  module$contents$goog$debug$Error_DebugError.call(this, opt_message);
};
goog.inherits(goog.Promise.CancellationError, module$contents$goog$debug$Error_DebugError);
goog.Promise.CancellationError.prototype.name = "cancel";
goog.Promise.Resolver_ = function(promise, resolve, reject) {
  this.promise = promise;
  this.resolve = resolve;
  this.reject = reject;
};
goog.Timer = function(opt_interval, opt_timerObject) {
  goog.events.EventTarget.call(this);
  this.interval_ = opt_interval || 1;
  this.timerObject_ = opt_timerObject || goog.Timer.defaultTimerObject;
  this.boundTick_ = goog.bind(this.tick_, this);
  this.last_ = goog.now();
};
goog.inherits(goog.Timer, goog.events.EventTarget);
goog.Timer.MAX_TIMEOUT_ = 2147483647;
goog.Timer.INVALID_TIMEOUT_ID_ = -1;
goog.Timer.prototype.enabled = !1;
goog.Timer.defaultTimerObject = goog.global;
goog.Timer.intervalScale = .8;
goog.Timer.prototype.timer_ = null;
goog.Timer.prototype.setInterval = function(interval) {
  this.interval_ = interval;
  this.timer_ && this.enabled ? (this.stop(), this.start()) : this.timer_ && this.stop();
};
goog.Timer.prototype.tick_ = function() {
  if (this.enabled) {
    var elapsed = goog.now() - this.last_;
    0 < elapsed && elapsed < this.interval_ * goog.Timer.intervalScale ? this.timer_ = this.timerObject_.setTimeout(this.boundTick_, this.interval_ - elapsed) : (this.timer_ && (this.timerObject_.clearTimeout(this.timer_), this.timer_ = null), this.dispatchTick(), this.enabled && (this.stop(), this.start()));
  }
};
goog.Timer.prototype.dispatchTick = function() {
  this.dispatchEvent(goog.Timer.TICK);
};
goog.Timer.prototype.start = function() {
  this.enabled = !0;
  this.timer_ || (this.timer_ = this.timerObject_.setTimeout(this.boundTick_, this.interval_), this.last_ = goog.now());
};
goog.Timer.prototype.stop = function() {
  this.enabled = !1;
  this.timer_ && (this.timerObject_.clearTimeout(this.timer_), this.timer_ = null);
};
goog.Timer.prototype.disposeInternal = function() {
  goog.Timer.superClass_.disposeInternal.call(this);
  this.stop();
  delete this.timerObject_;
};
goog.Timer.TICK = "tick";
goog.Timer.callOnce = function(listener, opt_delay, opt_handler) {
  if ("function" === typeof listener) {
    opt_handler && (listener = goog.bind(listener, opt_handler));
  } else if (listener && "function" == typeof listener.handleEvent) {
    listener = goog.bind(listener.handleEvent, listener);
  } else {
    throw Error("Invalid listener argument");
  }
  return Number(opt_delay) > goog.Timer.MAX_TIMEOUT_ ? goog.Timer.INVALID_TIMEOUT_ID_ : goog.Timer.defaultTimerObject.setTimeout(listener, opt_delay || 0);
};
goog.Timer.clear = function(timerId) {
  goog.Timer.defaultTimerObject.clearTimeout(timerId);
};
goog.Timer.promise = function(delay, opt_result) {
  var timerKey = null;
  return (new goog.Promise(function(resolve, reject) {
    timerKey = goog.Timer.callOnce(function() {
      resolve(opt_result);
    }, delay);
    timerKey == goog.Timer.INVALID_TIMEOUT_ID_ && reject(Error("Failed to schedule timer."));
  })).thenCatch(function(error) {
    goog.Timer.clear(timerKey);
    throw error;
  });
};
goog.uri = {};
goog.uri.utils = {};
goog.uri.utils.QueryArray = {};
goog.uri.utils.QueryValue = {};
goog.uri.utils.CharCode_ = {AMPERSAND:38, EQUAL:61, HASH:35, QUESTION:63};
goog.uri.utils.buildFromEncodedParts = function(opt_scheme, opt_userInfo, opt_domain, opt_port, opt_path, opt_queryData, opt_fragment) {
  var out = "";
  opt_scheme && (out += opt_scheme + ":");
  opt_domain && (out += "//", opt_userInfo && (out += opt_userInfo + "@"), out += opt_domain, opt_port && (out += ":" + opt_port));
  opt_path && (out += opt_path);
  opt_queryData && (out += "?" + opt_queryData);
  opt_fragment && (out += "#" + opt_fragment);
  return out;
};
goog.uri.utils.splitRe_ = RegExp("^(?:([^:/?#.]+):)?(?://(?:([^\\\\/?#]*)@)?([^\\\\/?#]*?)(?::([0-9]+))?(?=[\\\\/?#]|$))?([^?#]+)?(?:\\?([^#]*))?(?:#([\\s\\S]*))?$");
goog.uri.utils.ComponentIndex = {SCHEME:1, USER_INFO:2, DOMAIN:3, PORT:4, PATH:5, QUERY_DATA:6, FRAGMENT:7};
goog.uri.utils.urlPackageSupportLoggingHandler_ = null;
goog.uri.utils.setUrlPackageSupportLoggingHandler = function(handler) {
  goog.uri.utils.urlPackageSupportLoggingHandler_ = handler;
};
goog.uri.utils.split = function(uri) {
  var result = uri.match(goog.uri.utils.splitRe_);
  goog.uri.utils.urlPackageSupportLoggingHandler_ && 0 <= ["http", "https", "ws", "wss", "ftp"].indexOf(result[goog.uri.utils.ComponentIndex.SCHEME]) && goog.uri.utils.urlPackageSupportLoggingHandler_(uri);
  return result;
};
goog.uri.utils.decodeIfPossible_ = function(uri, opt_preserveReserved) {
  return uri ? opt_preserveReserved ? decodeURI(uri) : decodeURIComponent(uri) : uri;
};
goog.uri.utils.getComponentByIndex_ = function(componentIndex, uri) {
  return goog.uri.utils.split(uri)[componentIndex] || null;
};
goog.uri.utils.getScheme = function(uri) {
  return goog.uri.utils.getComponentByIndex_(goog.uri.utils.ComponentIndex.SCHEME, uri);
};
goog.uri.utils.getEffectiveScheme = function(uri) {
  var scheme = goog.uri.utils.getScheme(uri);
  if (!scheme && goog.global.self && goog.global.self.location) {
    var protocol = goog.global.self.location.protocol;
    scheme = protocol.slice(0, -1);
  }
  return scheme ? scheme.toLowerCase() : "";
};
goog.uri.utils.getUserInfoEncoded = function(uri) {
  return goog.uri.utils.getComponentByIndex_(goog.uri.utils.ComponentIndex.USER_INFO, uri);
};
goog.uri.utils.getUserInfo = function(uri) {
  return goog.uri.utils.decodeIfPossible_(goog.uri.utils.getUserInfoEncoded(uri));
};
goog.uri.utils.getDomainEncoded = function(uri) {
  return goog.uri.utils.getComponentByIndex_(goog.uri.utils.ComponentIndex.DOMAIN, uri);
};
goog.uri.utils.getDomain = function(uri) {
  return goog.uri.utils.decodeIfPossible_(goog.uri.utils.getDomainEncoded(uri), !0);
};
goog.uri.utils.getPort = function(uri) {
  return Number(goog.uri.utils.getComponentByIndex_(goog.uri.utils.ComponentIndex.PORT, uri)) || null;
};
goog.uri.utils.getPathEncoded = function(uri) {
  return goog.uri.utils.getComponentByIndex_(goog.uri.utils.ComponentIndex.PATH, uri);
};
goog.uri.utils.getPath = function(uri) {
  return goog.uri.utils.decodeIfPossible_(goog.uri.utils.getPathEncoded(uri), !0);
};
goog.uri.utils.getQueryData = function(uri) {
  return goog.uri.utils.getComponentByIndex_(goog.uri.utils.ComponentIndex.QUERY_DATA, uri);
};
goog.uri.utils.getFragmentEncoded = function(uri) {
  var hashIndex = uri.indexOf("#");
  return 0 > hashIndex ? null : uri.slice(hashIndex + 1);
};
goog.uri.utils.setFragmentEncoded = function(uri, fragment) {
  return goog.uri.utils.removeFragment(uri) + (fragment ? "#" + fragment : "");
};
goog.uri.utils.getFragment = function(uri) {
  return goog.uri.utils.decodeIfPossible_(goog.uri.utils.getFragmentEncoded(uri));
};
goog.uri.utils.getHost = function(uri) {
  var pieces = goog.uri.utils.split(uri);
  return goog.uri.utils.buildFromEncodedParts(pieces[goog.uri.utils.ComponentIndex.SCHEME], pieces[goog.uri.utils.ComponentIndex.USER_INFO], pieces[goog.uri.utils.ComponentIndex.DOMAIN], pieces[goog.uri.utils.ComponentIndex.PORT]);
};
goog.uri.utils.getOrigin = function(uri) {
  var pieces = goog.uri.utils.split(uri);
  return goog.uri.utils.buildFromEncodedParts(pieces[goog.uri.utils.ComponentIndex.SCHEME], null, pieces[goog.uri.utils.ComponentIndex.DOMAIN], pieces[goog.uri.utils.ComponentIndex.PORT]);
};
goog.uri.utils.getPathAndAfter = function(uri) {
  var pieces = goog.uri.utils.split(uri);
  return goog.uri.utils.buildFromEncodedParts(null, null, null, null, pieces[goog.uri.utils.ComponentIndex.PATH], pieces[goog.uri.utils.ComponentIndex.QUERY_DATA], pieces[goog.uri.utils.ComponentIndex.FRAGMENT]);
};
goog.uri.utils.removeFragment = function(uri) {
  var hashIndex = uri.indexOf("#");
  return 0 > hashIndex ? uri : uri.slice(0, hashIndex);
};
goog.uri.utils.haveSameDomain = function(uri1, uri2) {
  var pieces1 = goog.uri.utils.split(uri1), pieces2 = goog.uri.utils.split(uri2);
  return pieces1[goog.uri.utils.ComponentIndex.DOMAIN] == pieces2[goog.uri.utils.ComponentIndex.DOMAIN] && pieces1[goog.uri.utils.ComponentIndex.SCHEME] == pieces2[goog.uri.utils.ComponentIndex.SCHEME] && pieces1[goog.uri.utils.ComponentIndex.PORT] == pieces2[goog.uri.utils.ComponentIndex.PORT];
};
goog.uri.utils.assertNoFragmentsOrQueries_ = function(uri) {
  goog.asserts.assert(0 > uri.indexOf("#") && 0 > uri.indexOf("?"), "goog.uri.utils: Fragment or query identifiers are not supported: [%s]", uri);
};
goog.uri.utils.parseQueryData = function(encodedQuery, callback) {
  if (encodedQuery) {
    for (var pairs = encodedQuery.split("&"), i = 0; i < pairs.length; i++) {
      var indexOfEquals = pairs[i].indexOf("="), value = null;
      if (0 <= indexOfEquals) {
        var name = pairs[i].substring(0, indexOfEquals);
        value = pairs[i].substring(indexOfEquals + 1);
      } else {
        name = pairs[i];
      }
      callback(name, value ? goog.string.urlDecode(value) : "");
    }
  }
};
goog.uri.utils.splitQueryData_ = function(uri) {
  var hashIndex = uri.indexOf("#");
  0 > hashIndex && (hashIndex = uri.length);
  var questionIndex = uri.indexOf("?");
  if (0 > questionIndex || questionIndex > hashIndex) {
    questionIndex = hashIndex;
    var queryData = "";
  } else {
    queryData = uri.substring(questionIndex + 1, hashIndex);
  }
  return [uri.slice(0, questionIndex), queryData, uri.slice(hashIndex)];
};
goog.uri.utils.joinQueryData_ = function(parts) {
  return parts[0] + (parts[1] ? "?" + parts[1] : "") + parts[2];
};
goog.uri.utils.appendQueryData_ = function(queryData, newData) {
  return newData ? queryData ? queryData + "&" + newData : newData : queryData;
};
goog.uri.utils.appendQueryDataToUri_ = function(uri, queryData) {
  if (!queryData) {
    return uri;
  }
  var parts = goog.uri.utils.splitQueryData_(uri);
  parts[1] = goog.uri.utils.appendQueryData_(parts[1], queryData);
  return goog.uri.utils.joinQueryData_(parts);
};
goog.uri.utils.appendKeyValuePairs_ = function(key, value, pairs) {
  goog.asserts.assertString(key);
  if (Array.isArray(value)) {
    goog.asserts.assertArray(value);
    for (var j = 0; j < value.length; j++) {
      goog.uri.utils.appendKeyValuePairs_(key, String(value[j]), pairs);
    }
  } else {
    null != value && pairs.push(key + ("" === value ? "" : "=" + goog.string.urlEncode(value)));
  }
};
goog.uri.utils.buildQueryData = function(keysAndValues, opt_startIndex) {
  goog.asserts.assert(0 == Math.max(keysAndValues.length - (opt_startIndex || 0), 0) % 2, "goog.uri.utils: Key/value lists must be even in length.");
  for (var params = [], i = opt_startIndex || 0; i < keysAndValues.length; i += 2) {
    var key = keysAndValues[i];
    goog.uri.utils.appendKeyValuePairs_(key, keysAndValues[i + 1], params);
  }
  return params.join("&");
};
goog.uri.utils.buildQueryDataFromMap = function(map) {
  var params = [], key;
  for (key in map) {
    goog.uri.utils.appendKeyValuePairs_(key, map[key], params);
  }
  return params.join("&");
};
goog.uri.utils.appendParams = function(uri, var_args) {
  var queryData = 2 == arguments.length ? goog.uri.utils.buildQueryData(arguments[1], 0) : goog.uri.utils.buildQueryData(arguments, 1);
  return goog.uri.utils.appendQueryDataToUri_(uri, queryData);
};
goog.uri.utils.appendParamsFromMap = function(uri, map) {
  var queryData = goog.uri.utils.buildQueryDataFromMap(map);
  return goog.uri.utils.appendQueryDataToUri_(uri, queryData);
};
goog.uri.utils.appendParam = function(uri, key, opt_value) {
  var value = null != opt_value ? "=" + goog.string.urlEncode(opt_value) : "";
  return goog.uri.utils.appendQueryDataToUri_(uri, key + value);
};
goog.uri.utils.findParam_ = function(uri, startIndex, keyEncoded, hashOrEndIndex) {
  for (var index = startIndex, keyLength = keyEncoded.length; 0 <= (index = uri.indexOf(keyEncoded, index)) && index < hashOrEndIndex;) {
    var precedingChar = uri.charCodeAt(index - 1);
    if (precedingChar == goog.uri.utils.CharCode_.AMPERSAND || precedingChar == goog.uri.utils.CharCode_.QUESTION) {
      var followingChar = uri.charCodeAt(index + keyLength);
      if (!followingChar || followingChar == goog.uri.utils.CharCode_.EQUAL || followingChar == goog.uri.utils.CharCode_.AMPERSAND || followingChar == goog.uri.utils.CharCode_.HASH) {
        return index;
      }
    }
    index += keyLength + 1;
  }
  return -1;
};
goog.uri.utils.hashOrEndRe_ = /#|$/;
goog.uri.utils.hasParam = function(uri, keyEncoded) {
  return 0 <= goog.uri.utils.findParam_(uri, 0, keyEncoded, uri.search(goog.uri.utils.hashOrEndRe_));
};
goog.uri.utils.getParamValue = function(uri, keyEncoded) {
  var hashOrEndIndex = uri.search(goog.uri.utils.hashOrEndRe_), foundIndex = goog.uri.utils.findParam_(uri, 0, keyEncoded, hashOrEndIndex);
  if (0 > foundIndex) {
    return null;
  }
  var endPosition = uri.indexOf("&", foundIndex);
  if (0 > endPosition || endPosition > hashOrEndIndex) {
    endPosition = hashOrEndIndex;
  }
  foundIndex += keyEncoded.length + 1;
  return goog.string.urlDecode(uri.slice(foundIndex, -1 !== endPosition ? endPosition : 0));
};
goog.uri.utils.getParamValues = function(uri, keyEncoded) {
  for (var hashOrEndIndex = uri.search(goog.uri.utils.hashOrEndRe_), position = 0, foundIndex, result = []; 0 <= (foundIndex = goog.uri.utils.findParam_(uri, position, keyEncoded, hashOrEndIndex));) {
    position = uri.indexOf("&", foundIndex);
    if (0 > position || position > hashOrEndIndex) {
      position = hashOrEndIndex;
    }
    foundIndex += keyEncoded.length + 1;
    result.push(goog.string.urlDecode(uri.slice(foundIndex, Math.max(position, 0))));
  }
  return result;
};
goog.uri.utils.trailingQueryPunctuationRe_ = /[?&]($|#)/;
goog.uri.utils.removeParam = function(uri, keyEncoded) {
  for (var hashOrEndIndex = uri.search(goog.uri.utils.hashOrEndRe_), position = 0, foundIndex, buffer = []; 0 <= (foundIndex = goog.uri.utils.findParam_(uri, position, keyEncoded, hashOrEndIndex));) {
    buffer.push(uri.substring(position, foundIndex)), position = Math.min(uri.indexOf("&", foundIndex) + 1 || hashOrEndIndex, hashOrEndIndex);
  }
  buffer.push(uri.slice(position));
  return buffer.join("").replace(goog.uri.utils.trailingQueryPunctuationRe_, "$1");
};
goog.uri.utils.setParam = function(uri, keyEncoded, value) {
  return goog.uri.utils.appendParam(goog.uri.utils.removeParam(uri, keyEncoded), keyEncoded, value);
};
goog.uri.utils.setParamsFromMap = function(uri, params) {
  var parts = goog.uri.utils.splitQueryData_(uri), queryData = parts[1], buffer = [];
  queryData && queryData.split("&").forEach(function(pair) {
    var indexOfEquals = pair.indexOf("="), name = 0 <= indexOfEquals ? pair.slice(0, indexOfEquals) : pair;
    params.hasOwnProperty(name) || buffer.push(pair);
  });
  parts[1] = goog.uri.utils.appendQueryData_(buffer.join("&"), goog.uri.utils.buildQueryDataFromMap(params));
  return goog.uri.utils.joinQueryData_(parts);
};
goog.uri.utils.appendPath = function(baseUri, path) {
  goog.uri.utils.assertNoFragmentsOrQueries_(baseUri);
  goog.string.endsWith(baseUri, "/") && (baseUri = baseUri.slice(0, -1));
  goog.string.startsWith(path, "/") && (path = path.slice(1));
  return "" + baseUri + "/" + path;
};
goog.uri.utils.setPath = function(uri, path) {
  goog.string.startsWith(path, "/") || (path = "/" + path);
  var parts = goog.uri.utils.split(uri);
  return goog.uri.utils.buildFromEncodedParts(parts[goog.uri.utils.ComponentIndex.SCHEME], parts[goog.uri.utils.ComponentIndex.USER_INFO], parts[goog.uri.utils.ComponentIndex.DOMAIN], parts[goog.uri.utils.ComponentIndex.PORT], path, parts[goog.uri.utils.ComponentIndex.QUERY_DATA], parts[goog.uri.utils.ComponentIndex.FRAGMENT]);
};
goog.uri.utils.StandardQueryParam = {RANDOM:"zx"};
goog.uri.utils.makeUnique = function(uri) {
  return goog.uri.utils.setParam(uri, goog.uri.utils.StandardQueryParam.RANDOM, goog.string.getRandomString());
};
goog.net.XhrIo = function(opt_xmlHttpFactory) {
  goog.events.EventTarget.call(this);
  this.headers = new Map();
  this.xmlHttpFactory_ = opt_xmlHttpFactory || null;
  this.active_ = !1;
  this.xhrOptions_ = this.xhr_ = null;
  this.lastError_ = this.lastMethod_ = this.lastUri_ = "";
  this.inAbort_ = this.inOpen_ = this.inSend_ = this.errorDispatched_ = !1;
  this.timeoutInterval_ = 0;
  this.timeoutId_ = null;
  this.responseType_ = goog.net.XhrIo.ResponseType.DEFAULT;
  this.useXhr2Timeout_ = this.progressEventsEnabled_ = this.withCredentials_ = !1;
  this.trustToken_ = null;
};
goog.inherits(goog.net.XhrIo, goog.events.EventTarget);
goog.net.XhrIo.ResponseType = {DEFAULT:"", TEXT:"text", DOCUMENT:"document", BLOB:"blob", ARRAY_BUFFER:"arraybuffer",};
goog.net.XhrIo.prototype.logger_ = goog.log.getLogger("goog.net.XhrIo");
goog.net.XhrIo.CONTENT_TYPE_HEADER = "Content-Type";
goog.net.XhrIo.CONTENT_TRANSFER_ENCODING = "Content-Transfer-Encoding";
goog.net.XhrIo.HTTP_SCHEME_PATTERN = /^https?$/i;
goog.net.XhrIo.METHODS_WITH_FORM_DATA = ["POST", "PUT"];
goog.net.XhrIo.FORM_CONTENT_TYPE = "application/x-www-form-urlencoded;charset=utf-8";
goog.net.XhrIo.XHR2_TIMEOUT_ = "timeout";
goog.net.XhrIo.XHR2_ON_TIMEOUT_ = "ontimeout";
goog.net.XhrIo.sendInstances_ = [];
goog.net.XhrIo.send = function(url, opt_callback, opt_method, opt_content, opt_headers, opt_timeoutInterval, opt_withCredentials) {
  var x = new goog.net.XhrIo();
  goog.net.XhrIo.sendInstances_.push(x);
  opt_callback && x.listen(goog.net.EventType.COMPLETE, opt_callback);
  x.listenOnce(goog.net.EventType.READY, x.cleanupSend_);
  opt_timeoutInterval && x.setTimeoutInterval(opt_timeoutInterval);
  opt_withCredentials && x.setWithCredentials(opt_withCredentials);
  x.send(url, opt_method, opt_content, opt_headers);
  return x;
};
goog.net.XhrIo.cleanup = function() {
  for (var instances = goog.net.XhrIo.sendInstances_; instances.length;) {
    instances.pop().dispose();
  }
};
goog.net.XhrIo.protectEntryPoints = function(errorHandler) {
  goog.net.XhrIo.prototype.onReadyStateChangeEntryPoint_ = errorHandler.protectEntryPoint(goog.net.XhrIo.prototype.onReadyStateChangeEntryPoint_);
};
goog.net.XhrIo.prototype.cleanupSend_ = function() {
  this.dispose();
  module$contents$goog$array_remove(goog.net.XhrIo.sendInstances_, this);
};
goog.net.XhrIo.prototype.setTimeoutInterval = function(ms) {
  this.timeoutInterval_ = Math.max(0, ms);
};
goog.net.XhrIo.prototype.setWithCredentials = function(withCredentials) {
  this.withCredentials_ = withCredentials;
};
goog.net.XhrIo.prototype.setTrustToken = function(trustToken) {
  this.trustToken_ = trustToken;
};
goog.net.XhrIo.prototype.send = function(url, opt_method, opt_content, opt_headers) {
  if (this.xhr_) {
    throw Error("[goog.net.XhrIo] Object is active with another request=" + this.lastUri_ + "; newUri=" + url);
  }
  var method = opt_method ? opt_method.toUpperCase() : "GET";
  this.lastUri_ = url;
  this.lastError_ = "";
  this.lastMethod_ = method;
  this.errorDispatched_ = !1;
  this.active_ = !0;
  this.xhr_ = this.createXhr();
  this.xhrOptions_ = this.xmlHttpFactory_ ? this.xmlHttpFactory_.getOptions() : goog.net.XmlHttp.getOptions();
  this.xhr_.onreadystatechange = goog.bind(this.onReadyStateChange_, this);
  this.progressEventsEnabled_ && "onprogress" in this.xhr_ && (this.xhr_.onprogress = goog.bind(function(e) {
    this.onProgressHandler_(e, !0);
  }, this), this.xhr_.upload && (this.xhr_.upload.onprogress = goog.bind(this.onProgressHandler_, this)));
  try {
    goog.log.fine(this.logger_, this.formatMsg_("Opening Xhr")), this.inOpen_ = !0, this.xhr_.open(method, String(url), !0), this.inOpen_ = !1;
  } catch (err$26) {
    goog.log.fine(this.logger_, this.formatMsg_("Error opening Xhr: " + err$26.message));
    this.error_(goog.net.ErrorCode.EXCEPTION, err$26);
    return;
  }
  var content = opt_content || "", headers = new Map(this.headers);
  if (opt_headers) {
    if (Object.getPrototypeOf(opt_headers) === Object.prototype) {
      for (var key in opt_headers) {
        headers.set(key, opt_headers[key]);
      }
    } else if ("function" === typeof opt_headers.keys && "function" === typeof opt_headers.get) {
      for (var $jscomp$iter$5 = $jscomp.makeIterator(opt_headers.keys()), $jscomp$key$key = $jscomp$iter$5.next(); !$jscomp$key$key.done; $jscomp$key$key = $jscomp$iter$5.next()) {
        var key$27 = $jscomp$key$key.value;
        headers.set(key$27, opt_headers.get(key$27));
      }
    } else {
      throw Error("Unknown input type for opt_headers: " + String(opt_headers));
    }
  }
  var contentTypeKey = Array.from(headers.keys()).find(function(header) {
    return goog.string.caseInsensitiveEquals(goog.net.XhrIo.CONTENT_TYPE_HEADER, header);
  }), contentIsFormData = goog.global.FormData && content instanceof goog.global.FormData;
  !module$contents$goog$array_contains(goog.net.XhrIo.METHODS_WITH_FORM_DATA, method) || contentTypeKey || contentIsFormData || headers.set(goog.net.XhrIo.CONTENT_TYPE_HEADER, goog.net.XhrIo.FORM_CONTENT_TYPE);
  for (var $jscomp$iter$6 = $jscomp.makeIterator(headers), $jscomp$key$ = $jscomp$iter$6.next(); !$jscomp$key$.done; $jscomp$key$ = $jscomp$iter$6.next()) {
    var $jscomp$destructuring$var14 = $jscomp$key$.value, $jscomp$destructuring$var15 = $jscomp.makeIterator($jscomp$destructuring$var14), key$28 = $jscomp$destructuring$var15.next().value, value = $jscomp$destructuring$var15.next().value;
    this.xhr_.setRequestHeader(key$28, value);
  }
  this.responseType_ && (this.xhr_.responseType = this.responseType_);
  "withCredentials" in this.xhr_ && this.xhr_.withCredentials !== this.withCredentials_ && (this.xhr_.withCredentials = this.withCredentials_);
  if ("setTrustToken" in this.xhr_ && this.trustToken_) {
    try {
      this.xhr_.setTrustToken(this.trustToken_);
    } catch (err$29) {
      goog.log.fine(this.logger_, this.formatMsg_("Error SetTrustToken: " + err$29.message));
    }
  }
  try {
    this.cleanUpTimeoutTimer_(), 0 < this.timeoutInterval_ && (this.useXhr2Timeout_ = goog.net.XhrIo.shouldUseXhr2Timeout_(this.xhr_), goog.log.fine(this.logger_, this.formatMsg_("Will abort after " + this.timeoutInterval_ + "ms if incomplete, xhr2 " + this.useXhr2Timeout_)), this.useXhr2Timeout_ ? (this.xhr_[goog.net.XhrIo.XHR2_TIMEOUT_] = this.timeoutInterval_, this.xhr_[goog.net.XhrIo.XHR2_ON_TIMEOUT_] = goog.bind(this.timeout_, this)) : this.timeoutId_ = goog.Timer.callOnce(this.timeout_, this.timeoutInterval_, 
    this)), goog.log.fine(this.logger_, this.formatMsg_("Sending request")), this.inSend_ = !0, this.xhr_.send(content), this.inSend_ = !1;
  } catch (err$30) {
    goog.log.fine(this.logger_, this.formatMsg_("Send error: " + err$30.message)), this.error_(goog.net.ErrorCode.EXCEPTION, err$30);
  }
};
goog.net.XhrIo.shouldUseXhr2Timeout_ = function(xhr) {
  return goog.userAgent.IE && goog.userAgent.isVersionOrHigher(9) && "number" === typeof xhr[goog.net.XhrIo.XHR2_TIMEOUT_] && void 0 !== xhr[goog.net.XhrIo.XHR2_ON_TIMEOUT_];
};
goog.net.XhrIo.prototype.createXhr = function() {
  return this.xmlHttpFactory_ ? this.xmlHttpFactory_.createInstance() : goog.net.XmlHttp();
};
goog.net.XhrIo.prototype.timeout_ = function() {
  "undefined" != typeof goog && this.xhr_ && (this.lastError_ = "Timed out after " + this.timeoutInterval_ + "ms, aborting", goog.log.fine(this.logger_, this.formatMsg_(this.lastError_)), this.dispatchEvent(goog.net.EventType.TIMEOUT), this.abort(goog.net.ErrorCode.TIMEOUT));
};
goog.net.XhrIo.prototype.error_ = function(errorCode, err) {
  this.active_ = !1;
  this.xhr_ && (this.inAbort_ = !0, this.xhr_.abort(), this.inAbort_ = !1);
  this.lastError_ = err;
  this.dispatchErrors_();
  this.cleanUpXhr_();
};
goog.net.XhrIo.prototype.dispatchErrors_ = function() {
  this.errorDispatched_ || (this.errorDispatched_ = !0, this.dispatchEvent(goog.net.EventType.COMPLETE), this.dispatchEvent(goog.net.EventType.ERROR));
};
goog.net.XhrIo.prototype.abort = function() {
  this.xhr_ && this.active_ && (goog.log.fine(this.logger_, this.formatMsg_("Aborting")), this.active_ = !1, this.inAbort_ = !0, this.xhr_.abort(), this.inAbort_ = !1, this.dispatchEvent(goog.net.EventType.COMPLETE), this.dispatchEvent(goog.net.EventType.ABORT), this.cleanUpXhr_());
};
goog.net.XhrIo.prototype.disposeInternal = function() {
  this.xhr_ && (this.active_ && (this.active_ = !1, this.inAbort_ = !0, this.xhr_.abort(), this.inAbort_ = !1), this.cleanUpXhr_(!0));
  goog.net.XhrIo.superClass_.disposeInternal.call(this);
};
goog.net.XhrIo.prototype.onReadyStateChange_ = function() {
  if (!this.isDisposed()) {
    if (this.inOpen_ || this.inSend_ || this.inAbort_) {
      this.onReadyStateChangeHelper_();
    } else {
      this.onReadyStateChangeEntryPoint_();
    }
  }
};
goog.net.XhrIo.prototype.onReadyStateChangeEntryPoint_ = function() {
  this.onReadyStateChangeHelper_();
};
goog.net.XhrIo.prototype.onReadyStateChangeHelper_ = function() {
  if (this.active_ && "undefined" != typeof goog) {
    if (this.xhrOptions_[goog.net.XmlHttp.OptionType.LOCAL_REQUEST_ERROR] && this.getReadyState() == goog.net.XmlHttp.ReadyState.COMPLETE && 2 == this.getStatus()) {
      goog.log.fine(this.logger_, this.formatMsg_("Local request error detected and ignored"));
    } else {
      if (this.inSend_ && this.getReadyState() == goog.net.XmlHttp.ReadyState.COMPLETE) {
        goog.Timer.callOnce(this.onReadyStateChange_, 0, this);
      } else {
        if (this.dispatchEvent(goog.net.EventType.READY_STATE_CHANGE), this.isComplete()) {
          goog.log.fine(this.logger_, this.formatMsg_("Request complete"));
          this.active_ = !1;
          try {
            this.isSuccess() ? (this.dispatchEvent(goog.net.EventType.COMPLETE), this.dispatchEvent(goog.net.EventType.SUCCESS)) : (this.lastError_ = this.getStatusText() + " [" + this.getStatus() + "]", this.dispatchErrors_());
          } finally {
            this.cleanUpXhr_();
          }
        }
      }
    }
  }
};
goog.net.XhrIo.prototype.onProgressHandler_ = function(e, opt_isDownload) {
  goog.asserts.assert(e.type === goog.net.EventType.PROGRESS, "goog.net.EventType.PROGRESS is of the same type as raw XHR progress.");
  this.dispatchEvent(goog.net.XhrIo.buildProgressEvent_(e, goog.net.EventType.PROGRESS));
  this.dispatchEvent(goog.net.XhrIo.buildProgressEvent_(e, opt_isDownload ? goog.net.EventType.DOWNLOAD_PROGRESS : goog.net.EventType.UPLOAD_PROGRESS));
};
goog.net.XhrIo.buildProgressEvent_ = function(e, eventType) {
  return {type:eventType, lengthComputable:e.lengthComputable, loaded:e.loaded, total:e.total,};
};
goog.net.XhrIo.prototype.cleanUpXhr_ = function(opt_fromDispose) {
  if (this.xhr_) {
    this.cleanUpTimeoutTimer_();
    var xhr = this.xhr_, clearedOnReadyStateChange = this.xhrOptions_[goog.net.XmlHttp.OptionType.USE_NULL_FUNCTION] ? function() {
    } : null;
    this.xhrOptions_ = this.xhr_ = null;
    opt_fromDispose || this.dispatchEvent(goog.net.EventType.READY);
    try {
      xhr.onreadystatechange = clearedOnReadyStateChange;
    } catch (e) {
      goog.log.error(this.logger_, "Problem encountered resetting onreadystatechange: " + e.message);
    }
  }
};
goog.net.XhrIo.prototype.cleanUpTimeoutTimer_ = function() {
  this.xhr_ && this.useXhr2Timeout_ && (this.xhr_[goog.net.XhrIo.XHR2_ON_TIMEOUT_] = null);
  this.timeoutId_ && (goog.Timer.clear(this.timeoutId_), this.timeoutId_ = null);
};
goog.net.XhrIo.prototype.isActive = function() {
  return !!this.xhr_;
};
goog.net.XhrIo.prototype.isComplete = function() {
  return this.getReadyState() == goog.net.XmlHttp.ReadyState.COMPLETE;
};
goog.net.XhrIo.prototype.isSuccess = function() {
  var status = this.getStatus();
  return goog.net.HttpStatus.isSuccess(status) || 0 === status && !this.isLastUriEffectiveSchemeHttp_();
};
goog.net.XhrIo.prototype.isLastUriEffectiveSchemeHttp_ = function() {
  var scheme = goog.uri.utils.getEffectiveScheme(String(this.lastUri_));
  return goog.net.XhrIo.HTTP_SCHEME_PATTERN.test(scheme);
};
goog.net.XhrIo.prototype.getReadyState = function() {
  return this.xhr_ ? this.xhr_.readyState : goog.net.XmlHttp.ReadyState.UNINITIALIZED;
};
goog.net.XhrIo.prototype.getStatus = function() {
  try {
    return this.getReadyState() > goog.net.XmlHttp.ReadyState.LOADED ? this.xhr_.status : -1;
  } catch (e) {
    return -1;
  }
};
goog.net.XhrIo.prototype.getStatusText = function() {
  try {
    return this.getReadyState() > goog.net.XmlHttp.ReadyState.LOADED ? this.xhr_.statusText : "";
  } catch (e) {
    return goog.log.fine(this.logger_, "Can not get status: " + e.message), "";
  }
};
goog.net.XhrIo.prototype.getResponseText = function() {
  try {
    return this.xhr_ ? this.xhr_.responseText : "";
  } catch (e) {
    return goog.log.fine(this.logger_, "Can not get responseText: " + e.message), "";
  }
};
goog.net.XhrIo.prototype.getResponseHeader = function(key) {
  if (this.xhr_ && this.isComplete()) {
    var value = this.xhr_.getResponseHeader(key);
    return null === value ? void 0 : value;
  }
};
goog.net.XhrIo.prototype.getAllResponseHeaders = function() {
  return this.xhr_ && this.getReadyState() >= goog.net.XmlHttp.ReadyState.LOADED ? this.xhr_.getAllResponseHeaders() || "" : "";
};
goog.net.XhrIo.prototype.formatMsg_ = function(msg) {
  return msg + " [" + this.lastMethod_ + " " + this.lastUri_ + " " + this.getStatus() + "]";
};
goog.debug.entryPointRegistry.register(function(transformer) {
  goog.net.XhrIo.prototype.onReadyStateChangeEntryPoint_ = transformer(goog.net.XhrIo.prototype.onReadyStateChangeEntryPoint_);
});
goog.structs = {};
goog.structs.getCount = function(col) {
  return col.getCount && "function" == typeof col.getCount ? col.getCount() : goog.isArrayLike(col) || "string" === typeof col ? col.length : module$contents$goog$object_getCount(col);
};
goog.structs.getValues = function(col) {
  if (col.getValues && "function" == typeof col.getValues) {
    return col.getValues();
  }
  if ("undefined" !== typeof Map && col instanceof Map || "undefined" !== typeof Set && col instanceof Set) {
    return Array.from(col.values());
  }
  if ("string" === typeof col) {
    return col.split("");
  }
  if (goog.isArrayLike(col)) {
    for (var rv = [], l = col.length, i = 0; i < l; i++) {
      rv.push(col[i]);
    }
    return rv;
  }
  return module$contents$goog$object_getValues(col);
};
goog.structs.getKeys = function(col) {
  if (col.getKeys && "function" == typeof col.getKeys) {
    return col.getKeys();
  }
  if (!col.getValues || "function" != typeof col.getValues) {
    if ("undefined" !== typeof Map && col instanceof Map) {
      return Array.from(col.keys());
    }
    if (!("undefined" !== typeof Set && col instanceof Set)) {
      if (goog.isArrayLike(col) || "string" === typeof col) {
        for (var rv = [], l = col.length, i = 0; i < l; i++) {
          rv.push(i);
        }
        return rv;
      }
      return module$contents$goog$object_getKeys(col);
    }
  }
};
goog.structs.contains = function(col, val) {
  return col.contains && "function" == typeof col.contains ? col.contains(val) : col.containsValue && "function" == typeof col.containsValue ? col.containsValue(val) : goog.isArrayLike(col) || "string" === typeof col ? module$contents$goog$array_contains(col, val) : module$contents$goog$object_containsValue(col, val);
};
goog.structs.isEmpty = function(col) {
  return col.isEmpty && "function" == typeof col.isEmpty ? col.isEmpty() : goog.isArrayLike(col) || "string" === typeof col ? 0 === col.length : module$contents$goog$object_isEmpty(col);
};
goog.structs.clear = function(col) {
  col.clear && "function" == typeof col.clear ? col.clear() : goog.isArrayLike(col) ? module$contents$goog$array_clear(col) : module$contents$goog$object_clear(col);
};
goog.structs.forEach = function(col, f, opt_obj) {
  if (col.forEach && "function" == typeof col.forEach) {
    col.forEach(f, opt_obj);
  } else if (goog.isArrayLike(col) || "string" === typeof col) {
    Array.prototype.forEach.call(col, f, opt_obj);
  } else {
    for (var keys = goog.structs.getKeys(col), values = goog.structs.getValues(col), l = values.length, i = 0; i < l; i++) {
      f.call(opt_obj, values[i], keys && keys[i], col);
    }
  }
};
goog.structs.filter = function(col, f, opt_obj) {
  if ("function" == typeof col.filter) {
    return col.filter(f, opt_obj);
  }
  if (goog.isArrayLike(col) || "string" === typeof col) {
    return Array.prototype.filter.call(col, f, opt_obj);
  }
  var keys = goog.structs.getKeys(col), values = goog.structs.getValues(col), l = values.length;
  if (keys) {
    var rv = {};
    for (var i = 0; i < l; i++) {
      f.call(opt_obj, values[i], keys[i], col) && (rv[keys[i]] = values[i]);
    }
  } else {
    for (rv = [], i = 0; i < l; i++) {
      f.call(opt_obj, values[i], void 0, col) && rv.push(values[i]);
    }
  }
  return rv;
};
goog.structs.map = function(col, f, opt_obj) {
  if ("function" == typeof col.map) {
    return col.map(f, opt_obj);
  }
  if (goog.isArrayLike(col) || "string" === typeof col) {
    return Array.prototype.map.call(col, f, opt_obj);
  }
  var keys = goog.structs.getKeys(col), values = goog.structs.getValues(col), l = values.length;
  if (keys) {
    var rv = {};
    for (var i = 0; i < l; i++) {
      rv[keys[i]] = f.call(opt_obj, values[i], keys[i], col);
    }
  } else {
    for (rv = [], i = 0; i < l; i++) {
      rv[i] = f.call(opt_obj, values[i], void 0, col);
    }
  }
  return rv;
};
goog.structs.some = function(col, f, opt_obj) {
  if ("function" == typeof col.some) {
    return col.some(f, opt_obj);
  }
  if (goog.isArrayLike(col) || "string" === typeof col) {
    return Array.prototype.some.call(col, f, opt_obj);
  }
  for (var keys = goog.structs.getKeys(col), values = goog.structs.getValues(col), l = values.length, i = 0; i < l; i++) {
    if (f.call(opt_obj, values[i], keys && keys[i], col)) {
      return !0;
    }
  }
  return !1;
};
goog.structs.every = function(col, f, opt_obj) {
  if ("function" == typeof col.every) {
    return col.every(f, opt_obj);
  }
  if (goog.isArrayLike(col) || "string" === typeof col) {
    return Array.prototype.every.call(col, f, opt_obj);
  }
  for (var keys = goog.structs.getKeys(col), values = goog.structs.getValues(col), l = values.length, i = 0; i < l; i++) {
    if (!f.call(opt_obj, values[i], keys && keys[i], col)) {
      return !1;
    }
  }
  return !0;
};
goog.Uri = function(opt_uri, opt_ignoreCase) {
  this.domain_ = this.userInfo_ = this.scheme_ = "";
  this.port_ = null;
  this.fragment_ = this.path_ = "";
  this.ignoreCase_ = this.isReadOnly_ = !1;
  var m;
  opt_uri instanceof goog.Uri ? (this.ignoreCase_ = void 0 !== opt_ignoreCase ? opt_ignoreCase : opt_uri.ignoreCase_, this.setScheme(opt_uri.getScheme()), this.setUserInfo(opt_uri.getUserInfo()), this.setDomain(opt_uri.getDomain()), this.setPort(opt_uri.getPort()), this.setPath(opt_uri.getPath()), this.setQueryData(opt_uri.getQueryData().clone()), this.setFragment(opt_uri.getFragment())) : opt_uri && (m = goog.uri.utils.split(String(opt_uri))) ? (this.ignoreCase_ = !!opt_ignoreCase, this.setScheme(m[goog.uri.utils.ComponentIndex.SCHEME] || 
  "", !0), this.setUserInfo(m[goog.uri.utils.ComponentIndex.USER_INFO] || "", !0), this.setDomain(m[goog.uri.utils.ComponentIndex.DOMAIN] || "", !0), this.setPort(m[goog.uri.utils.ComponentIndex.PORT]), this.setPath(m[goog.uri.utils.ComponentIndex.PATH] || "", !0), this.setQueryData(m[goog.uri.utils.ComponentIndex.QUERY_DATA] || "", !0), this.setFragment(m[goog.uri.utils.ComponentIndex.FRAGMENT] || "", !0)) : (this.ignoreCase_ = !!opt_ignoreCase, this.queryData_ = new goog.Uri.QueryData(null, this.ignoreCase_));
};
goog.Uri.RANDOM_PARAM = goog.uri.utils.StandardQueryParam.RANDOM;
goog.Uri.prototype.toString = function() {
  var out = [], scheme = this.getScheme();
  scheme && out.push(goog.Uri.encodeSpecialChars_(scheme, goog.Uri.reDisallowedInSchemeOrUserInfo_, !0), ":");
  var domain = this.getDomain();
  if (domain || "file" == scheme) {
    out.push("//");
    var userInfo = this.getUserInfo();
    userInfo && out.push(goog.Uri.encodeSpecialChars_(userInfo, goog.Uri.reDisallowedInSchemeOrUserInfo_, !0), "@");
    out.push(goog.Uri.removeDoubleEncoding_(goog.string.urlEncode(domain)));
    var port = this.getPort();
    null != port && out.push(":", String(port));
  }
  var path = this.getPath();
  path && (this.hasDomain() && "/" != path.charAt(0) && out.push("/"), out.push(goog.Uri.encodeSpecialChars_(path, "/" == path.charAt(0) ? goog.Uri.reDisallowedInAbsolutePath_ : goog.Uri.reDisallowedInRelativePath_, !0)));
  var query = this.getEncodedQuery();
  query && out.push("?", query);
  var fragment = this.getFragment();
  fragment && out.push("#", goog.Uri.encodeSpecialChars_(fragment, goog.Uri.reDisallowedInFragment_));
  return out.join("");
};
goog.Uri.prototype.resolve = function(relativeUri) {
  var absoluteUri = this.clone(), overridden = relativeUri.hasScheme();
  overridden ? absoluteUri.setScheme(relativeUri.getScheme()) : overridden = relativeUri.hasUserInfo();
  overridden ? absoluteUri.setUserInfo(relativeUri.getUserInfo()) : overridden = relativeUri.hasDomain();
  overridden ? absoluteUri.setDomain(relativeUri.getDomain()) : overridden = relativeUri.hasPort();
  var path = relativeUri.getPath();
  if (overridden) {
    absoluteUri.setPort(relativeUri.getPort());
  } else {
    if (overridden = relativeUri.hasPath()) {
      if ("/" != path.charAt(0)) {
        if (this.hasDomain() && !this.hasPath()) {
          path = "/" + path;
        } else {
          var lastSlashIndex = absoluteUri.getPath().lastIndexOf("/");
          -1 != lastSlashIndex && (path = absoluteUri.getPath().slice(0, lastSlashIndex + 1) + path);
        }
      }
      path = goog.Uri.removeDotSegments(path);
    }
  }
  overridden ? absoluteUri.setPath(path) : overridden = relativeUri.hasQuery();
  overridden ? absoluteUri.setQueryData(relativeUri.getQueryData().clone()) : overridden = relativeUri.hasFragment();
  overridden && absoluteUri.setFragment(relativeUri.getFragment());
  return absoluteUri;
};
goog.Uri.prototype.clone = function() {
  return new goog.Uri(this);
};
goog.Uri.prototype.getScheme = function() {
  return this.scheme_;
};
goog.Uri.prototype.setScheme = function(newScheme, opt_decode) {
  this.enforceReadOnly();
  if (this.scheme_ = opt_decode ? goog.Uri.decodeOrEmpty_(newScheme, !0) : newScheme) {
    this.scheme_ = this.scheme_.replace(/:$/, "");
  }
  return this;
};
goog.Uri.prototype.hasScheme = function() {
  return !!this.scheme_;
};
goog.Uri.prototype.getUserInfo = function() {
  return this.userInfo_;
};
goog.Uri.prototype.setUserInfo = function(newUserInfo, opt_decode) {
  this.enforceReadOnly();
  this.userInfo_ = opt_decode ? goog.Uri.decodeOrEmpty_(newUserInfo) : newUserInfo;
  return this;
};
goog.Uri.prototype.hasUserInfo = function() {
  return !!this.userInfo_;
};
goog.Uri.prototype.getDomain = function() {
  return this.domain_;
};
goog.Uri.prototype.setDomain = function(newDomain, opt_decode) {
  this.enforceReadOnly();
  this.domain_ = opt_decode ? goog.Uri.decodeOrEmpty_(newDomain, !0) : newDomain;
  return this;
};
goog.Uri.prototype.hasDomain = function() {
  return !!this.domain_;
};
goog.Uri.prototype.getPort = function() {
  return this.port_;
};
goog.Uri.prototype.setPort = function(newPort) {
  this.enforceReadOnly();
  if (newPort) {
    newPort = Number(newPort);
    if (isNaN(newPort) || 0 > newPort) {
      throw Error("Bad port number " + newPort);
    }
    this.port_ = newPort;
  } else {
    this.port_ = null;
  }
  return this;
};
goog.Uri.prototype.hasPort = function() {
  return null != this.port_;
};
goog.Uri.prototype.getPath = function() {
  return this.path_;
};
goog.Uri.prototype.setPath = function(newPath, opt_decode) {
  this.enforceReadOnly();
  this.path_ = opt_decode ? goog.Uri.decodeOrEmpty_(newPath, !0) : newPath;
  return this;
};
goog.Uri.prototype.hasPath = function() {
  return !!this.path_;
};
goog.Uri.prototype.hasQuery = function() {
  return "" !== this.queryData_.toString();
};
goog.Uri.prototype.setQueryData = function(queryData, opt_decode) {
  this.enforceReadOnly();
  queryData instanceof goog.Uri.QueryData ? (this.queryData_ = queryData, this.queryData_.setIgnoreCase(this.ignoreCase_)) : (opt_decode || (queryData = goog.Uri.encodeSpecialChars_(queryData, goog.Uri.reDisallowedInQuery_)), this.queryData_ = new goog.Uri.QueryData(queryData, this.ignoreCase_));
  return this;
};
goog.Uri.prototype.getEncodedQuery = function() {
  return this.queryData_.toString();
};
goog.Uri.prototype.getQueryData = function() {
  return this.queryData_;
};
goog.Uri.prototype.getQuery = function() {
  return this.getEncodedQuery();
};
goog.Uri.prototype.setParameterValue = function(key, value) {
  this.enforceReadOnly();
  this.queryData_.set(key, value);
  return this;
};
goog.Uri.prototype.getFragment = function() {
  return this.fragment_;
};
goog.Uri.prototype.setFragment = function(newFragment, opt_decode) {
  this.enforceReadOnly();
  this.fragment_ = opt_decode ? goog.Uri.decodeOrEmpty_(newFragment) : newFragment;
  return this;
};
goog.Uri.prototype.hasFragment = function() {
  return !!this.fragment_;
};
goog.Uri.prototype.makeUnique = function() {
  this.enforceReadOnly();
  this.setParameterValue(goog.Uri.RANDOM_PARAM, goog.string.getRandomString());
  return this;
};
goog.Uri.prototype.removeParameter = function(key) {
  this.enforceReadOnly();
  this.queryData_.remove(key);
  return this;
};
goog.Uri.prototype.enforceReadOnly = function() {
  if (this.isReadOnly_) {
    throw Error("Tried to modify a read-only Uri");
  }
};
goog.Uri.prototype.setIgnoreCase = function(ignoreCase) {
  this.ignoreCase_ = ignoreCase;
  this.queryData_ && this.queryData_.setIgnoreCase(ignoreCase);
  return this;
};
goog.Uri.parse = function(uri, opt_ignoreCase) {
  return uri instanceof goog.Uri ? uri.clone() : new goog.Uri(uri, opt_ignoreCase);
};
goog.Uri.create = function(opt_scheme, opt_userInfo, opt_domain, opt_port, opt_path, opt_query, opt_fragment, opt_ignoreCase) {
  var uri = new goog.Uri(null, opt_ignoreCase);
  opt_scheme && uri.setScheme(opt_scheme);
  opt_userInfo && uri.setUserInfo(opt_userInfo);
  opt_domain && uri.setDomain(opt_domain);
  opt_port && uri.setPort(opt_port);
  opt_path && uri.setPath(opt_path);
  opt_query && uri.setQueryData(opt_query);
  opt_fragment && uri.setFragment(opt_fragment);
  return uri;
};
goog.Uri.resolve = function(base, rel) {
  base instanceof goog.Uri || (base = goog.Uri.parse(base));
  rel instanceof goog.Uri || (rel = goog.Uri.parse(rel));
  return base.resolve(rel);
};
goog.Uri.removeDotSegments = function(path) {
  if (".." == path || "." == path) {
    return "";
  }
  if (goog.string.contains(path, "./") || goog.string.contains(path, "/.")) {
    for (var leadingSlash = goog.string.startsWith(path, "/"), segments = path.split("/"), out = [], pos = 0; pos < segments.length;) {
      var segment = segments[pos++];
      "." == segment ? leadingSlash && pos == segments.length && out.push("") : ".." == segment ? ((1 < out.length || 1 == out.length && "" != out[0]) && out.pop(), leadingSlash && pos == segments.length && out.push("")) : (out.push(segment), leadingSlash = !0);
    }
    return out.join("/");
  }
  return path;
};
goog.Uri.decodeOrEmpty_ = function(val, opt_preserveReserved) {
  return val ? opt_preserveReserved ? decodeURI(val.replace(/%25/g, "%2525")) : decodeURIComponent(val) : "";
};
goog.Uri.encodeSpecialChars_ = function(unescapedPart, extra, opt_removeDoubleEncoding) {
  if ("string" === typeof unescapedPart) {
    var encoded = encodeURI(unescapedPart).replace(extra, goog.Uri.encodeChar_);
    opt_removeDoubleEncoding && (encoded = goog.Uri.removeDoubleEncoding_(encoded));
    return encoded;
  }
  return null;
};
goog.Uri.encodeChar_ = function(ch) {
  var n = ch.charCodeAt(0);
  return "%" + (n >> 4 & 15).toString(16) + (n & 15).toString(16);
};
goog.Uri.removeDoubleEncoding_ = function(doubleEncodedString) {
  return doubleEncodedString.replace(/%25([0-9a-fA-F]{2})/g, "%$1");
};
goog.Uri.reDisallowedInSchemeOrUserInfo_ = /[#\/\?@]/g;
goog.Uri.reDisallowedInRelativePath_ = /[#\?:]/g;
goog.Uri.reDisallowedInAbsolutePath_ = /[#\?]/g;
goog.Uri.reDisallowedInQuery_ = /[#\?@]/g;
goog.Uri.reDisallowedInFragment_ = /#/g;
goog.Uri.haveSameDomain = function(uri1String, uri2String) {
  var pieces1 = goog.uri.utils.split(uri1String), pieces2 = goog.uri.utils.split(uri2String);
  return pieces1[goog.uri.utils.ComponentIndex.DOMAIN] == pieces2[goog.uri.utils.ComponentIndex.DOMAIN] && pieces1[goog.uri.utils.ComponentIndex.PORT] == pieces2[goog.uri.utils.ComponentIndex.PORT];
};
goog.Uri.QueryData = function(opt_query, opt_ignoreCase) {
  this.count_ = this.keyMap_ = null;
  this.encodedQuery_ = opt_query || null;
  this.ignoreCase_ = !!opt_ignoreCase;
};
goog.Uri.QueryData.prototype.ensureKeyMapInitialized_ = function() {
  if (!this.keyMap_ && (this.keyMap_ = new Map(), this.count_ = 0, this.encodedQuery_)) {
    var self = this;
    goog.uri.utils.parseQueryData(this.encodedQuery_, function(name, value) {
      self.add(goog.string.urlDecode(name), value);
    });
  }
};
goog.Uri.QueryData.createFromMap = function(map, opt_ignoreCase) {
  var keys = goog.structs.getKeys(map);
  if ("undefined" == typeof keys) {
    throw Error("Keys are undefined");
  }
  for (var queryData = new goog.Uri.QueryData(null, opt_ignoreCase), values = goog.structs.getValues(map), i = 0; i < keys.length; i++) {
    var key = keys[i], value = values[i];
    Array.isArray(value) ? queryData.setValues(key, value) : queryData.add(key, value);
  }
  return queryData;
};
goog.Uri.QueryData.createFromKeysValues = function(keys, values, opt_ignoreCase) {
  if (keys.length != values.length) {
    throw Error("Mismatched lengths for keys/values");
  }
  for (var queryData = new goog.Uri.QueryData(null, opt_ignoreCase), i = 0; i < keys.length; i++) {
    queryData.add(keys[i], values[i]);
  }
  return queryData;
};
goog.Uri.QueryData.prototype.getCount = function() {
  this.ensureKeyMapInitialized_();
  return this.count_;
};
goog.Uri.QueryData.prototype.add = function(key, value) {
  this.ensureKeyMapInitialized_();
  this.invalidateCache_();
  key = this.getKeyName_(key);
  var values = this.keyMap_.get(key);
  values || this.keyMap_.set(key, values = []);
  values.push(value);
  this.count_ = goog.asserts.assertNumber(this.count_) + 1;
  return this;
};
goog.Uri.QueryData.prototype.remove = function(key) {
  this.ensureKeyMapInitialized_();
  key = this.getKeyName_(key);
  return this.keyMap_.has(key) ? (this.invalidateCache_(), this.count_ = goog.asserts.assertNumber(this.count_) - this.keyMap_.get(key).length, this.keyMap_.delete(key)) : !1;
};
goog.Uri.QueryData.prototype.clear = function() {
  this.invalidateCache_();
  this.keyMap_ = null;
  this.count_ = 0;
};
goog.Uri.QueryData.prototype.isEmpty = function() {
  this.ensureKeyMapInitialized_();
  return 0 == this.count_;
};
goog.Uri.QueryData.prototype.containsKey = function(key) {
  this.ensureKeyMapInitialized_();
  key = this.getKeyName_(key);
  return this.keyMap_.has(key);
};
goog.Uri.QueryData.prototype.containsValue = function(value) {
  var vals = this.getValues();
  return module$contents$goog$array_contains(vals, value);
};
goog.Uri.QueryData.prototype.forEach = function(f, opt_scope) {
  this.ensureKeyMapInitialized_();
  this.keyMap_.forEach(function(values, key) {
    values.forEach(function(value) {
      f.call(opt_scope, value, key, this);
    }, this);
  }, this);
};
goog.Uri.QueryData.prototype.getKeys = function() {
  this.ensureKeyMapInitialized_();
  for (var vals = Array.from(this.keyMap_.values()), keys = Array.from(this.keyMap_.keys()), rv = [], i = 0; i < keys.length; i++) {
    for (var val = vals[i], j = 0; j < val.length; j++) {
      rv.push(keys[i]);
    }
  }
  return rv;
};
goog.Uri.QueryData.prototype.getValues = function(opt_key) {
  this.ensureKeyMapInitialized_();
  var rv = [];
  if ("string" === typeof opt_key) {
    this.containsKey(opt_key) && (rv = rv.concat(this.keyMap_.get(this.getKeyName_(opt_key))));
  } else {
    for (var values = Array.from(this.keyMap_.values()), i = 0; i < values.length; i++) {
      rv = rv.concat(values[i]);
    }
  }
  return rv;
};
goog.Uri.QueryData.prototype.set = function(key, value) {
  this.ensureKeyMapInitialized_();
  this.invalidateCache_();
  key = this.getKeyName_(key);
  this.containsKey(key) && (this.count_ = goog.asserts.assertNumber(this.count_) - this.keyMap_.get(key).length);
  this.keyMap_.set(key, [value]);
  this.count_ = goog.asserts.assertNumber(this.count_) + 1;
  return this;
};
goog.Uri.QueryData.prototype.get = function(key, opt_default) {
  if (!key) {
    return opt_default;
  }
  var values = this.getValues(key);
  return 0 < values.length ? String(values[0]) : opt_default;
};
goog.Uri.QueryData.prototype.setValues = function(key, values) {
  this.remove(key);
  0 < values.length && (this.invalidateCache_(), this.keyMap_.set(this.getKeyName_(key), module$contents$goog$array_toArray(values)), this.count_ = goog.asserts.assertNumber(this.count_) + values.length);
};
goog.Uri.QueryData.prototype.toString = function() {
  if (this.encodedQuery_) {
    return this.encodedQuery_;
  }
  if (!this.keyMap_) {
    return "";
  }
  for (var sb = [], keys = Array.from(this.keyMap_.keys()), i = 0; i < keys.length; i++) {
    for (var key = keys[i], encodedKey = goog.string.urlEncode(key), val = this.getValues(key), j = 0; j < val.length; j++) {
      var param = encodedKey;
      "" !== val[j] && (param += "=" + goog.string.urlEncode(val[j]));
      sb.push(param);
    }
  }
  return this.encodedQuery_ = sb.join("&");
};
goog.Uri.QueryData.prototype.invalidateCache_ = function() {
  this.encodedQuery_ = null;
};
goog.Uri.QueryData.prototype.clone = function() {
  var rv = new goog.Uri.QueryData();
  rv.encodedQuery_ = this.encodedQuery_;
  this.keyMap_ && (rv.keyMap_ = new Map(this.keyMap_), rv.count_ = this.count_);
  return rv;
};
goog.Uri.QueryData.prototype.getKeyName_ = function(arg) {
  var keyName = String(arg);
  this.ignoreCase_ && (keyName = keyName.toLowerCase());
  return keyName;
};
goog.Uri.QueryData.prototype.setIgnoreCase = function(ignoreCase) {
  var resetKeys = ignoreCase && !this.ignoreCase_;
  resetKeys && (this.ensureKeyMapInitialized_(), this.invalidateCache_(), this.keyMap_.forEach(function(value, key) {
    var lowerCase = key.toLowerCase();
    key != lowerCase && (this.remove(key), this.setValues(lowerCase, value));
  }, this));
  this.ignoreCase_ = ignoreCase;
};
goog.Uri.QueryData.prototype.extend = function(var_args) {
  for (var i = 0; i < arguments.length; i++) {
    var data = arguments[i];
    goog.structs.forEach(data, function(value, key) {
      this.add(key, value);
    }, this);
  }
};
goog.appengine = {};
goog.appengine.DevChannel = function(token) {
  this.token_ = token;
};
goog.appengine.DevChannel.prototype.open = function(opt_handler) {
  opt_handler = opt_handler || new goog.appengine.DevSocket.Handler();
  return new goog.appengine.DevSocket(this.token_, opt_handler);
};
goog.appengine.DevSocket = function(token, handler) {
  this.readyState = goog.appengine.DevSocket.ReadyState.CONNECTING;
  this.token_ = token;
  this.applicationKey_ = token.substring(token.lastIndexOf("-") + 1);
  this.clientId_ = null;
  this.onopen = handler.onopen;
  this.onmessage = handler.onmessage;
  this.onerror = handler.onerror;
  this.onclose = handler.onclose;
  this.win_ = goog.dom.getWindow();
  this.pollingTimer_ = null;
  goog.net.XhrIo.send(this.getUrl_("connect"), goog.bind(this.connect_, this));
  goog.events.listen(this.win_, "beforeunload", goog.bind(this.beforeunload_, this));
  if (!document.body) {
    throw "document.body is not defined -- do not create socket from script in <head>.";
  }
};
goog.appengine.DevSocket.prototype.getUrl_ = function(command) {
  var url = goog.appengine.DevSocket.BASE_URL + "dev?command=" + command + "&channel=" + this.token_;
  this.clientId_ && (url += "&client=" + this.clientId_);
  return url;
};
goog.appengine.DevSocket.prototype.connect_ = function(e) {
  var xhr = e.target;
  if (xhr.isSuccess()) {
    this.clientId_ = xhr.getResponseText(), this.readyState = goog.appengine.DevSocket.ReadyState.OPEN, this.onopen(), this.pollingTimer_ = this.win_.setTimeout(goog.bind(this.poll_, this), goog.appengine.DevSocket.POLLING_TIMEOUT_MS);
  } else {
    this.readyState = goog.appengine.DevSocket.ReadyState.CLOSING;
    var evt = {};
    evt.description = xhr.getStatusText();
    evt.code = xhr.getStatus();
    this.onerror(evt);
    this.readyState = goog.appengine.DevSocket.ReadyState.CLOSED;
    this.onclose();
  }
};
goog.appengine.DevSocket.prototype.disconnect_ = function() {
  this.readyState = goog.appengine.DevSocket.ReadyState.CLOSED;
  this.onclose();
};
goog.appengine.DevSocket.prototype.forwardMessage_ = function(e) {
  var xhr = e.target;
  if (xhr.isSuccess()) {
    var evt = {};
    evt.data = xhr.getResponseText();
    if (evt.data.length) {
      this.onmessage(evt);
    }
    this.readyState == goog.appengine.DevSocket.ReadyState.OPEN && (this.pollingTimer_ = this.win_.setTimeout(goog.bind(this.poll_, this), goog.appengine.DevSocket.POLLING_TIMEOUT_MS));
  } else {
    evt = {}, evt.description = xhr.getStatusText(), evt.code = xhr.getStatus(), this.onerror(evt), this.readyState = goog.appengine.DevSocket.ReadyState.CLOSED, this.onclose();
  }
};
goog.appengine.DevSocket.prototype.poll_ = function() {
  goog.net.XhrIo.send(this.getUrl_("poll"), goog.bind(this.forwardMessage_, this));
};
goog.appengine.DevSocket.prototype.beforeunload_ = function() {
  var xhr = goog.net.XmlHttp();
  xhr.open("GET", this.getUrl_("disconnect"), !1);
  xhr.send();
};
goog.appengine.DevSocket.prototype.forwardSendComplete_ = function(e) {
  var xhr = e.target;
  if (!xhr.isSuccess()) {
    var evt = {};
    evt.description = xhr.getStatusText();
    evt.code = xhr.getStatus();
    this.onerror(evt);
  }
};
goog.appengine.DevSocket.prototype.send = function(data) {
  if (this.readyState != goog.appengine.DevSocket.ReadyState.OPEN) {
    return !1;
  }
  var url = goog.appengine.DevSocket.BASE_URL + "receive", sendData = new goog.Uri.QueryData();
  sendData.set("key", this.applicationKey_);
  sendData.set("msg", data);
  goog.net.XhrIo.send(url, goog.bind(this.forwardSendComplete_, this), "POST", sendData.toString());
  return !0;
};
goog.appengine.DevSocket.prototype.close = function() {
  this.readyState = goog.appengine.DevSocket.ReadyState.CLOSING;
  this.pollingTimer_ && this.win_.clearTimeout(this.pollingTimer_);
  goog.net.XhrIo.send(this.getUrl_("disconnect"), goog.bind(this.disconnect_, this));
};
goog.appengine.DevSocket.POLLING_TIMEOUT_MS = 500;
goog.appengine.DevSocket.BASE_URL = "/_ah/channel/";
goog.appengine.DevSocket.ReadyState = {CONNECTING:0, OPEN:1, CLOSING:2, CLOSED:3};
goog.appengine.DevSocket.Handler = function() {
};
goog.appengine.DevSocket.Handler.prototype.onopen = function() {
};
goog.appengine.DevSocket.Handler.prototype.onmessage = function() {
};
goog.appengine.DevSocket.Handler.prototype.onerror = function() {
};
goog.appengine.DevSocket.Handler.prototype.onclose = function() {
};
goog.exportSymbol("goog.appengine.Channel", goog.appengine.DevChannel);
goog.exportSymbol("goog.appengine.Channel.prototype.open", goog.appengine.DevChannel.prototype.open);
goog.exportSymbol("goog.appengine.Socket.Handler", goog.appengine.DevSocket.Handler);
goog.exportSymbol("goog.appengine.Socket.Handler.prototype.onopen", goog.appengine.DevChannel.prototype.onopen);
goog.exportSymbol("goog.appengine.Socket.Handler.prototype.onmessage", goog.appengine.DevSocket.Handler.prototype.onmessage);
goog.exportSymbol("goog.appengine.Socket.Handler.prototype.onerror", goog.appengine.DevSocket.Handler.prototype.onerror);
goog.exportSymbol("goog.appengine.Socket.Handler.prototype.onclose", goog.appengine.DevSocket.Handler.prototype.onclose);
goog.exportSymbol("goog.appengine.Socket", goog.appengine.DevSocket);
goog.exportSymbol("goog.appengine.Socket.ReadyState", goog.appengine.DevSocket.ReadyState);
goog.exportSymbol("goog.appengine.Socket.prototype.send", goog.appengine.DevSocket.prototype.send);
goog.exportSymbol("goog.appengine.Socket.prototype.close", goog.appengine.DevSocket.prototype.close);
}).call(this);
