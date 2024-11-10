# From NAND to Tetris: Part 2

This project is an implementation of the second part of the
"From NAND to Tetris" course, which aims to teach computer
science from the ground up by building a complete,
working computer system from basic logic gates.
This project covers the software side of the computer
system, including assembler, virtual machine, the operating
system and the compiler.


import org.rocksdb.*;

public class BlobDBBenchmark {

    static {
        RocksDB.loadLibrary();
    }

    public static void main(String[] args) {
        Options options = new Options();
        options.setCreateIfMissing(true);
        
        // Enable BlobDB features
        options.setEnableBlobFiles(true);
        options.setMinBlobSize(4096); // Example: Only store values > 4 KB in BlobDB
        options.setBlobFileSize(1024 * 1024 * 128); // Example: Max blob file size 128 MB
        options.setEnableBlobGarbageCollection(true);
        options.setBlobGarbageCollectionAgeCutoff(0.25); // 25% of the blob file must be obsolete to trigger GC
        
        try (RocksDB db = RocksDB.open(options, "path/to/db")) {
            // Test data loading
            long startTime = System.currentTimeMillis();
            
            for (int i = 0; i < 100000; i++) {
                byte[] key = ("key" + i).getBytes();
                byte[] value = new byte[8192]; // 8 KB value, stored in blob files
                db.put(key, value);
            }

            long endTime = System.currentTimeMillis();
            System.out.println("Data Insertion Time: " + (endTime - startTime) + " ms");

            // Test data retrieval
            startTime = System.currentTimeMillis();
            
            for (int i = 0; i < 100000; i++) {
                byte[] key = ("key" + i).getBytes();
                db.get(key);
            }

            endTime = System.currentTimeMillis();
            System.out.println("Data Retrieval Time: " + (endTime - startTime) + " ms");

        } catch (RocksDBException e) {
            System.err.println("Error working with RocksDB: " + e.getMessage());
        } finally {
            options.close();
        }
    }
}


import org.rocksdb.*;

public class FRocksDBBenchmark {

    static {
        RocksDB.loadLibrary();
    }

    public static void main(String[] args) {
        Options options = new Options();
        options.setCreateIfMissing(true);

        // Enable BlobDB features in FRocksDB, similar to RocksDB
        options.setEnableBlobFiles(true);
        options.setMinBlobSize(4096); // Set minimum blob size, e.g., 4 KB
        options.setBlobFileSize(1024 * 1024 * 128); // Set blob file size, e.g., 128 MB
        options.setEnableBlobGarbageCollection(true);
        options.setBlobGarbageCollectionAgeCutoff(0.25); // 25% cutoff for GC

        try (RocksDB db = RocksDB.open(options, "path/to/frocksdb_benchmark")) {
            // Benchmark write performance
            long startTime = System.currentTimeMillis();
            
            for (int i = 0; i < 100000; i++) {
                byte[] key = ("key" + i).getBytes();
                byte[] value = new byte[8192]; // 8 KB value, to be stored in blob files
                db.put(key, value);
            }

            long endTime = System.currentTimeMillis();
            System.out.println("Data Insertion Time: " + (endTime - startTime) + " ms");

            // Benchmark read performance
            startTime = System.currentTimeMillis();
            
            for (int i = 0; i < 100000; i++) {
                byte[] key = ("key" + i).getBytes();
                db.get(key);
            }

            endTime = System.currentTimeMillis();
            System.out.println("Data Retrieval Time: " + (endTime - startTime) + " ms");

        } catch (RocksDBException e) {
            System.err.println("Error working with FRocksDB: " + e.getMessage());
        } finally {
            options.close();
        }
    }
}


