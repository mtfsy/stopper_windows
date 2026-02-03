"""
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_file_too_large(self, mock_getsize, mock_exists):
        """Test that ValueError is raised if file > 5MB."""
        mock_exists.return_value = True
        mock_getsize.return_value = 6 * 1024 * 1024  # 6MB
        with self.assertRaises(ValueError):
            FileValidator.check_req("big_file.txt")

    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_invalid_extension(self, mock_getsize, mock_exists):
        """Test that TypeError is raised for non-.txt files."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        with self.assertRaises(TypeError):
            FileValidator.check_req("document.pdf")

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open)
    def test_corrupted_file(self, mock_file, mock_getsize, mock_exists):
        """Test that RuntimeError is raised on encoding issues."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        # Simulate a UnicodeDecodeError when reading
        mock_file.return_value.read.side_effect = UnicodeDecodeError('utf-8', b'', 0, 1, 'invalid')
        
        with self.assertRaises(RuntimeError):
            FileValidator.check_req("corrupt.txt")

    @patch('os.path.exists')
    @patch('os.path.getsize')
    @patch('builtins.open', new_callable=mock_open, read_data="valid content")
    def test_success_path(self, mock_file, mock_getsize, mock_exists):
        """Test that the function returns success for a valid file."""
        mock_exists.return_value = True
        mock_getsize.return_value = 1024
        
        result = FileValidator.check_req("valid_file.txt")
        self.assertEqual(result, "Success: File meets all requirements.")



    # Test the File Requirement Check
    @patch('os.path.exists')
    @patch('os.path.getsize')
    def test_check_req_file_not_found(self, mock_size, mock_exists):
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            Task.check_req("fake_file.txt")
    
    # Test the Kill Program Logic (Windows Mock)
    

    # Test the Task Interval Logic
    def test_task_should_run(self):
        # Create a task with 10s interval, 0 delay
        task = Task("Test", lambda x: print(x), "data", 10, 0)
        
        # 5 seconds later... should NOT run
        self.assertFalse(task.should_run(task.start_time + 5))
        
        # 11 seconds later... SHOULD run
        self.assertTrue(task.should_run(task.start_time + 11))
        """