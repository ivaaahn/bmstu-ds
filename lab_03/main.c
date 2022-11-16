#include <stdio.h>
#include <stdint.h>
#include <sys/stat.h>
#include <stdlib.h>
#include <string.h>
#include "tables.h"

#define BUFF_SIZE 1024
#define LSHIFT_28BIT(x, L) ((((x) << (L)) | ((x) >> (-(L) & 27))) & (((uint64_t)1 << 32) - 1))



size_t DES(uint8_t * to, uint8_t mode, uint8_t * key8b, uint8_t * from, size_t length);

void key_expansion(uint64_t key64b, uint64_t * keys48b);
void key_permutation_56bits_to_28bits(uint64_t block56b, uint32_t * block32b_1, uint32_t * block32b_2);
void key_expansion_to_48bits(uint32_t block28b_1, uint32_t block28b_2, uint64_t * keys48b);
uint64_t key_contraction_permutation(uint64_t block56b);

void feistel_cipher(uint8_t mode, uint32_t * N1, uint32_t * N2, uint64_t * keys48b);
void round_feistel_cipher(uint32_t * N1, uint32_t * N2, uint64_t key48b);
uint32_t func_F(uint32_t block32b, uint64_t key48b);
uint64_t expansion_permutation(uint32_t block32b);
uint32_t substitutions(uint64_t block48b);
void substitution_6bits_to_4bits(uint8_t * blocks6b, uint8_t * blocks4b);
uint32_t permutation(uint32_t block32b);

uint8_t extreme_bits(uint8_t block6b);
uint8_t middle_bits(uint8_t block6b);

uint64_t initial_permutation(uint64_t block64b);
uint64_t final_permutation(uint64_t block64b);

void split_64bits_to_32bits(uint64_t block64b, uint32_t * block32b_1, uint32_t * block32b_2);
void split_64bits_to_8bits(uint64_t block64b, uint8_t * blocks8b);
void split_48bits_to_6bits(uint64_t block48b, uint8_t * blocks6b);

uint64_t join_32bits_to_64bits(uint32_t block32b_1, uint32_t block32b_2);
uint64_t join_28bits_to_56bits(uint32_t block28b_1, uint32_t block28b_2);
uint64_t join_8bytes_to_64bits(uint8_t * blocks8b);
uint32_t join_4bits_to_32bits(uint8_t * blocks4b);

static inline size_t input_string(uint8_t * buffer);
static inline void swap(uint32_t * N1, uint32_t * N2);
static inline void print_array(uint8_t * array, size_t length);
static inline void print_bits(uint64_t x, register uint64_t Nbit);
size_t read_file(char *filename, uint8_t **buffer);

// key, mode, path
int main(int argc, char **argv) {
    uint8_t key_as_array_8b[8] = "DESkey56";
    char mode = 'E';
    char path[128] = {0};

    if (argc == 1) {
        printf("Не указан путь к файлу.");
        return 1;
    }

    if (strncpy(path, argv[1], 128) == 0) {
        puts("Ошибка");
        return 2;
    } else {
        printf("Использую файл: %s \n", path);
    }

    if (argc < 3) {
        printf("Не указан ключ шифрования. Использую ключ по умолчанию: %s \n", key_as_array_8b);

    }

    if (argc >= 3) { // указан ключ
        strncpy(key_as_array_8b, argv[2], 8);
        printf("Использую ключ: %s \n", key_as_array_8b);
    }

    if (argc < 4) {
        puts("Не указан режим работы. Шифрую...\n");
    }

    if (argc >= 4) { // указан режим
        if (strcmp(argv[3], "-D") == 0) {
            mode = 'D';
            puts("Дешифрую...\n");
        } else if (strcmp(argv[3], "-E") == 0) {
            mode = 'E';
            puts("Шифрую...\n");
        }
        else{
            puts("Некорректный режим работы..\n");
            return 3;
        }
    }

    uint8_t *file_buffer = NULL;
    size_t length = read_file(path, &file_buffer);

    uint8_t *result_buffer = NULL;
    result_buffer = malloc(length);

    length = DES(result_buffer, mode, key_as_array_8b, file_buffer, length);

    FILE *f = fopen("result", "wb");
    fwrite(result_buffer, length, 1, f);
    fclose(f);

    return 0;
}

size_t DES(uint8_t * to, uint8_t mode, uint8_t * key8b, uint8_t * from, size_t length) {
//    Выравниваем длину под блок 8 байт
    length = length % 8 == 0 ? length : length + (8 - (length % 8));

//    16 раундовых ключей по 48бит
    uint64_t keys48b[16] = {0};

//    Левый и правый блоки
    uint32_t N1, N2;

//    на вход 64 битный ключ, в результате получим 16 раундовых ключей по 48 бит
    key_expansion(
            join_8bytes_to_64bits(key8b), // переводим ключ в uint64
            keys48b
    );

    for (size_t i = 0; i < length; i += 8) {
//        просто сплитит на два N1 и N2
        split_64bits_to_32bits(
//               Восемь 8битовых значений конкатенируем в int64 и делаем начальную перестановку
                initial_permutation(join_8bytes_to_64bits(from + i)),
                &N1,
                &N2
        );
        feistel_cipher(mode, &N1, &N2, keys48b);
        split_64bits_to_8bits(
                final_permutation(join_32bits_to_64bits(N1, N2)),
                (to + i)
        );
    }

    return length;
}

//------------
// forth flow
//------------
//start:  Л П
//1 П ЛШ
//2 ЛШ ПШ
//3 ПШ ЛШШ
//4 ЛШШ ПШШ
//back swap: ПШШ ЛШШ
//result: ПШШ ЛШШ


//------------
// back flow
//------------
//start: ПШШ ЛШШ
//4 ЛШШ ПШ
//3 ПШ ЛШ
//2 ЛШ П
//1 П Л
//back swap: Л П
//result: Л П



void feistel_cipher(uint8_t mode, uint32_t * N1, uint32_t * N2, uint64_t * keys48b) {
    switch(mode) {
        case 'E': case 'e': {
            for (int8_t round = 0; round < 16; ++round) {
                round_feistel_cipher(N1, N2, keys48b[round]);
            }
//            внутри и так свопаем, лишний раз убираем
            swap(N1, N2);
            break;
        }
        case 'D': case 'd': {
            for (int8_t round = 15; round >= 0; --round) {
                round_feistel_cipher(N1, N2, keys48b[round]);
            }
            swap(N1, N2);
            break;
        }
    }
}

void round_feistel_cipher(uint32_t * N1, uint32_t * N2, uint64_t key48b) {
//    выполнить F и своп
    uint32_t temp = *N2;
    *N2 = func_F(*N2, key48b) ^ *N1;
    *N1 = temp;
}

uint32_t func_F(uint32_t block32b, uint64_t key48b) {
//    задача - расширить блок с 32 до 48 бит -- расширяющая перестановка (E)
    uint64_t block48b = expansion_permutation(block32b);
//    складываем с ключем и пропускаем через S блоки, чтобы получить на выходе 32 битовый блок
    block48b ^= key48b;
    block32b = substitutions(block48b);

//    перестановка (P)
    return permutation(block32b);
}

uint64_t expansion_permutation(uint32_t block32b) {
//    Аналогично, только расширяем (правые 16 битов будут нулевые, так как до 48 расщиряем)
    uint64_t block48b = 0;
    for (uint8_t i = 0 ; i < 48; ++i) {
        block48b |= (uint64_t)((block32b >> (32 - __EP[i])) & 0x01) << (63 - i);
    }
    return block48b;
}

uint32_t substitutions(uint64_t block48b) {
//    8 блоков по 6 бит и 8 блоков по 4 бита, но делаю 4 блока и уплотняю
    uint8_t blocks4b[4], blocks6b[8] = {0};
//    делим 48 битовый блок на блоки по 6 бит
    split_48bits_to_6bits(block48b, blocks6b);
//  делаем подстановку
    substitution_6bits_to_4bits(blocks6b, blocks4b);

//    соединяем 8 4ехбитных блоков в 32бита
    return join_4bits_to_32bits(blocks4b);
}

void substitution_6bits_to_4bits(uint8_t * blocks6b, uint8_t * blocks4b) {
//    на входе 6 битовый блок
    uint8_t block2b, block4b;

//    i += 2
    for (uint8_t i = 0, j = 0; i < 8; i += 2, ++j) {
//      берем крайние 2 бита (строка)
        block2b = extreme_bits(blocks6b[i]);

//      берем средние 4 бита (столбец)
        block4b = middle_bits(blocks6b[i]);

        blocks4b[j] = __Sbox[i][block2b][block4b];

//      Уплотняю сразу
        block2b = extreme_bits(blocks6b[i+1]);
        block4b = middle_bits(blocks6b[i+1]);
        blocks4b[j] = (blocks4b[j] << 4) | __Sbox[i+1][block2b][block4b];
    }
}

uint8_t extreme_bits(uint8_t block6b) {
    return ((block6b >> 6) & 0x2) | ((block6b >> 2) & 0x1);
}

uint8_t middle_bits(uint8_t block6b) {
    return (block6b >> 3) & 0xF;
}

uint32_t permutation(uint32_t block32b) {
//    просто по таблице перестановки
    uint32_t new_block32b = 0;
    for (uint8_t i = 0 ; i < 32; ++i) {
        new_block32b |= ((block32b >> (32 - __PP[i])) & 0x01) << (31 - i);
    }
    return new_block32b;
}

uint64_t initial_permutation(uint64_t block64b) {
//    Начальная переставновка,
// сдвигаем, засекаем нужный битик по таблице IP и ставим на текущую позицию
    uint64_t new_block64b = 0;
    for (uint8_t i = 0 ; i < 64; ++i) {
        new_block64b |= ((block64b >> (64 - __IP[i])) & 0x01) << (63 - i);
    }
    return new_block64b;
}

uint64_t final_permutation(uint64_t block64b) {
//    Аналогично выше
    uint64_t new_block64b = 0;
    for (uint8_t i = 0 ; i < 64; ++i) {
        new_block64b |= ((block64b >> (64 - __FP[i])) & 0x01) << (63 - i);
    }
    return new_block64b;
}

void key_expansion(uint64_t key64b, uint64_t * keys48b) {
//    Левая и правая части ключа по 28 бит
    uint32_t K1 = 0, K2 = 0;

//  Перестановка + Удаление битов четности + Разбиваем на две части
    key_permutation_56bits_to_28bits(key64b, &K1, &K2);
//    Основная функция расширения до 16 ключей по 48 бит
    key_expansion_to_48bits(K1, K2, keys48b);
}

void key_permutation_56bits_to_28bits(uint64_t block56b, uint32_t * block28b_1, uint32_t * block28b_2) {
    for (uint8_t i = 0; i < 28; ++i) {
        *block28b_1 |= ((block56b >> (64 - __K1P[i])) & 0x01) << (31 - i);
        *block28b_2 |= ((block56b >> (64 - __K2P[i])) & 0x01) << (31 - i);
    }
}
// Расширяем наш 56битный ключ до 16 ключей в 48 бит
void key_expansion_to_48bits(uint32_t block28b_1, uint32_t block28b_2, uint64_t * keys48b) {
    uint64_t block56b;
    uint8_t n;

    for (uint8_t i = 0; i < 16; ++i) {
        switch(i) {
//          сдвигаем либо на два влево, либо на 1
            case 0: case 1: case 8: case 15: n = 1; break;
            default: n = 2; break;
        }

//        Сдвиги Si
        block28b_1 = LSHIFT_28BIT(block28b_1, n);
        block28b_2 = LSHIFT_28BIT(block28b_2, n);

//        Склеиваем в 56 бит (Ci + Di)
        block56b = join_28bits_to_56bits(block28b_1, block28b_2);

        // Сжимающая перестановка CP 56бит -> 48бит
        keys48b[i] = key_contraction_permutation(block56b);
    }
}

uint64_t key_contraction_permutation(uint64_t block56b) {
    uint64_t block48b = 0;
    for (uint8_t i = 0 ; i < 48; ++i) {
        block48b |= ((block56b >> (64 - __CP[i])) & 0x01) << (63 - i);
    }
    return block48b;
}

void split_64bits_to_32bits(uint64_t block64b, uint32_t * block32b_1, uint32_t * block32b_2) {
    *block32b_1 = (uint32_t)(block64b >> 32);
    *block32b_2 = (uint32_t)(block64b);
}

void split_64bits_to_8bits(uint64_t block64b, uint8_t * blocks8b) {
    for (size_t i = 0; i < 8; ++i) {
        blocks8b[i] = (uint8_t)(block64b >> ((7 - i) * 8));
    }
}

void split_48bits_to_6bits(uint64_t block48b, uint8_t * blocks6b) {
//    64 - 6 == 58
    for (uint8_t i = 0; i < 8; ++i) {
        blocks6b[i] = (block48b >> (58 - (i * 6))) << 2; // так как unit8_t
    }
}


uint64_t join_32bits_to_64bits(uint32_t block32b_1, uint32_t block32b_2) {
    uint64_t block64b;
    block64b = (uint64_t)block32b_1;
    block64b = (uint64_t)(block64b << 32) | block32b_2;
    return block64b;
}

uint64_t join_28bits_to_56bits(uint32_t block28b_1, uint32_t block28b_2) {
    uint64_t block56b;
    block56b = (block28b_1 >> 4);
    block56b = ((block56b << 32) | block28b_2) << 4;
    return block56b;
}

// 8 байт == 64 бита. Проходим по всем восьмеркам, каждую вставляем в конец и сдвигаем влево.
uint64_t join_8bytes_to_64bits(uint8_t * blocks8b) {
    uint64_t block64b;
    for (uint8_t *p = blocks8b; p < blocks8b + 8; ++p) {
        block64b = (block64b << 8) | *p;
    }
    return block64b;
}

uint32_t join_4bits_to_32bits(uint8_t * blocks4b) {
    uint32_t block32b;
    for (uint8_t *p = blocks4b; p < blocks4b + 4; ++p) {
        block32b = (block32b << 8) | *p;
    }
    return block32b;
}

size_t read_file(char *filename, uint8_t* *file_buffer) {
    struct stat info;
    if (stat(filename, &info) != 0) {
        printf("error");
        return 1;
    }
    printf("FILE SIZE: %lu\n", (unsigned long)info.st_size);

    *file_buffer = malloc(info.st_size);
    if (*file_buffer == NULL) {
        printf("error");
    }
    FILE *fp = fopen(filename, "rb");
    if (fp == NULL) {
        printf("error");
    }

/* Try to read a single block of info.st_size bytes */
    size_t blocks_read = fread(*file_buffer, info.st_size, 1, fp);
    fclose(fp);

/*
 * If nothing went wrong, content now contains the
 * data read from the file.
 */

    printf("DATA LENGTH: %lu\n", (unsigned long)info.st_size);


    return (unsigned long)info.st_size;
}

static inline size_t input_string(uint8_t * buffer) {
    size_t position = 0;
    uint8_t ch;
    while ((ch = getchar()) != '\n' && position < BUFF_SIZE - 1)
        buffer[position++] = ch;
    buffer[position] = '\0';
    return position;
}

static inline void swap(uint32_t * N1, uint32_t * N2) {
    uint32_t temp = *N1;
    *N1 = *N2;
    *N2 = temp;
}

static inline void print_array(uint8_t * array, size_t length) {
    printf("[ ");
    for (size_t i = 0; i < length; ++i)
        printf("%d ", array[i]);
    printf("]\n");
}

static inline void print_bits(uint64_t x, register uint64_t Nbit) {
    for (Nbit = (uint64_t)1 << (Nbit - 1); Nbit > 0x00; Nbit >>= 1)
        printf("%d", (x & Nbit) ? 1 : 0);
    putchar('\n');
}