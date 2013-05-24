//============================
// regexplib
// ver: 0.11
//============================
正式更名为regexplib。修改了原先interval的一个小bug。
去掉了一些没用的调试语句。

这个库和上个版本一样，不会有任何版权，既然发布出来了，就是给大家分享的。
本人也是看了regexp和rx的代码，才把理论转化为实际的，所以，既然索取了，就有义务付出。


w3ishi
http://spaces.msn.com/w3ishi
w3ishi@gmail.com
2006-4-8


//============================
// reg.cpp
// ver: 0.1
//============================

与gnu rx, regexp 的regcomp(&reg, regstr, REG_EXTENDED)兼容。
gnu rx-1.5（目前最高版本）有一个bug：

char *string = "aaa";
char *pattern = "((a*)*)(\\1)";

出现bug时，syntax tree如下：
														r_concat
														/		\
													r_parens   	r_cset
														/
													r_star
													/
												r_parens
												/
											r_concat
											/	\
           						r_star	r_star
										/			\
									r_cset			r_cset

进入某些情况的递归分解时会产成死循环，本人给rx的作者Tom Lord写信询问这个问题，但并没有得到答复。regexp没有这个问题，reg.cpp解决了这个问题。

另外，regexp和rx对待(\number)这种匹配模式时可能会产生不同的sub expression匹配结果，我不知道哪里可以找到相应的标准，所以，本人的结果与rx相同。

匹配{m,n}模式时，由于个人的懒惰，并没有处理m或n其中一个没有给定的情况，哪位有时间可以自行更改RegExpBuild函数。

这个正则表达式库没有进行任何优化，所以可能并不具备rx或regexp的性能，目前公认性能最好的应该是regexp。但实现原理基本都是一样的:dfa, nfa, 递归分解猜测(Henry Spencer最早发明的？)。

写这个库的目的是为了个人练习，同时与对这方面感兴趣的朋友一同分享，毕竟rx与regexp的代码都略微不好读懂。reg.cpp应该不会有这种情况。


因为测试有限，能力有限，技术有限，头脑有限，所以不能保证这个库没有任何bug，如果它错误的格式化了您的硬盘本人概不负责。同时，这个库也没有任何版权，您可以任意修改使用。

w3ishi
w3ishi@gmail.com
2006年1月