/*
 * Name:	c2f.c
 * Desc:	print the table Celsius and Fahrenheit temperatures with head
 * Usage:	$>gcc c2f.c -o c2f
 *			$>./c2f
 * Author:	zuohaitao
 * Date:	2009 09 03
 */

#include <stdio.h>
int main()
{
	float fahr, celsius;
	float lower, upper, step;
	lower = 0;
	upper = 150;
	step = 10;

	celsius = lower;

	while ( celsius <= upper)
	{
		fahr = (9.0/5.0) * celsius + 32.0;
		printf("%6.1f %7.1f\n", celsius, fahr);
		celsius = celsius + step;
	}
}
