#ifndef MXBMSE_H
#define MXBMSE_H
/* 
  mxbmse -- Fast Boyer Moore Search Algorithm (Version 0.8)

  The implementation is reentrant and thread safe. While the
  general idea behind the Boyer Moore algorithm are in the public
  domain, this implementation falls under the following copyright:

  Copyright (c) 1997-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
  Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com

                        All Rights Reserved

  See the documentation for copying information or contact the author
  (mal@lemburg.com).

*/

#ifdef __cplusplus
extern "C" {
#endif

/* --- Fast Boyer-Moore Implementation (8-bit) ---------------------------- */

/* sanity check switches */
/*#define SAFER 1*/

/* BM_LENGTH_TYPE must have enough bits to store len(match)
   - using 'char' here makes the routines run 15% slower than
     with 'int', on the other hand, 
   - 'int' is at least 4 times larger than 'char'
   - 'long' is better on 64-bit CPUs
*/
#ifndef BM_LENGTH_TYPE
# define BM_LENGTH_TYPE int
#endif
#ifndef BM_INDEX_TYPE
# define BM_INDEX_TYPE BM_LENGTH_TYPE
#endif
#ifndef BM_SHIFT_TYPE
# define BM_SHIFT_TYPE BM_LENGTH_TYPE
#endif

typedef struct {
    char *match;
    BM_LENGTH_TYPE match_len;
    char *eom;
    char *pt;
    BM_SHIFT_TYPE shift[256]; /* char-based shift table */
} mxbmse_data;

extern mxbmse_data *bm_init(char *match,
			    BM_LENGTH_TYPE match_len);
extern void bm_free(mxbmse_data *c);
extern BM_INDEX_TYPE bm_search(mxbmse_data *c,
			       char *text,
			       BM_INDEX_TYPE start,
			       BM_LENGTH_TYPE text_len);
extern BM_INDEX_TYPE bm_tr_search(mxbmse_data *c,
				  char *text,
				  BM_INDEX_TYPE start,
				  BM_LENGTH_TYPE text_len,
				  char *tr);

#define BM_MATCH_LEN(bm) ((mxbmse_data *)bm)->match_len

/* EOF */
#ifdef __cplusplus
}
#endif
#endif
